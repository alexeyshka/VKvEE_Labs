import sys
import os
import math
from comtrade_reader import ComtradeReader

class FaultDetector:

    def __init__(self, db_path, oscillogram_id):
        self.db_path = db_path
        self.oscillogram_id = oscillogram_id
        self.db = ComtradeReader(db_path)
        self.cfg_data = {}
        self.channels = []
        self.samples_data = {}
        self.has_current = False
        self.has_voltage = False
        self.current_channels = []
        self.voltage_channels = []
        self.frequency = 50.0
        self.sampling_rate = 0.0
        self.samples_per_cycle = 0

    def load_from_db(self):

        # Получаем информацию об осциллограмме
        info = self.db.get_oscillogram_info(self.oscillogram_id)

        self.cfg_data = info
        self.frequency = info.get('frequency', 50.0)
        self.sampling_rate = 2400.0  # Стандартная частота дискретизации
        self.channels = self.db.get_channels(self.oscillogram_id) # Каналы файла с осциллограммой

        # Определяем наличие токов и напряжений
        self._identify_channels()

        # Загружаем выборки для всех каналов
        for channel in self.channels:
            ch_idx = channel['channel_index']
            samples = self.db.get_samples(self.oscillogram_id, channel_index=ch_idx)
            self.samples_data[ch_idx] = samples

        # Вычисляем количество выборок за период
        if self.frequency > 0:
            self.samples_per_cycle = int(self.sampling_rate / self.frequency)

        return True

    def _identify_channels(self):

        self.current_channels = []
        self.voltage_channels = []
        self.has_current = False
        self.has_voltage = False

        for channel in self.channels:
            if channel['channel_type'] != 'A':
                continue

            unit_lower = channel['unit'].lower()

            is_current = (
                    unit_lower == 'a' or
                    unit_lower == 'ka'
            )

            is_voltage = (
                    unit_lower == 'v' or
                    unit_lower == 'kv'
            )

            if is_current and is_voltage:
                if unit_lower in ['v', 'kv']:
                    is_current = False
                elif unit_lower in ['a', 'ka']:
                    is_voltage = False

            if is_current:
                self.current_channels.append(channel['channel_index'])
                self.has_current = True
            elif is_voltage:
                self.voltage_channels.append(channel['channel_index'])
                self.has_voltage = True

    def fourier_filter(self, samples, n_samples):
        if len(samples) < n_samples:
            return (0.0, 0.0)

        real_part = 0.0
        imag_part = 0.0

        for k in range(n_samples):
            angle = 2.0 * math.pi * k / n_samples
            real_part += samples[k] * math.cos(angle)
            imag_part -= samples[k] * math.sin(angle)

        real_part *= 2.0 / n_samples
        imag_part *= 2.0 / n_samples

        amplitude = math.sqrt(real_part ** 2 + imag_part ** 2)
        phase_angle = math.atan2(imag_part, real_part)

        return (amplitude, phase_angle)

    def calculate_rms_sliding(self, samples, window_size):
        if len(samples) < window_size:
            return []

        results = []
        values = [s['value'] for s in samples]

        for i in range(len(samples) - window_size + 1):
            window = values[i:i + window_size]
            amplitude, _ = self.fourier_filter(window, window_size)
            rms = amplitude / math.sqrt(2)
            results.append((samples[i]['sample_number'], rms))
        return results

    def calculate_impedance(self, voltage_rms, current_rms):
        """
        Расчет сопротивления по напряжениям и токам.
        """
        impedance = []
        current_dict = {sample_num: rms for sample_num, rms in current_rms}

        for sample_num, v_rms in voltage_rms:
            if sample_num in current_dict:
                i_rms = current_dict[sample_num]
                if i_rms > 0.001:
                    z = v_rms / i_rms
                    impedance.append((sample_num, z))

        return impedance

    # Расчет уставки по нормальному режиму (без КЗ).
    def calculate_setting(self, rms_values, is_current=True):

        if not rms_values:
            return 0.0

        normal_samples_count = max(1, len(rms_values) // 10)
        normal_values = [rms for _, rms in rms_values[:normal_samples_count]]

        if not normal_values:
            return 0.0

        avg_normal = sum(normal_values) / len(normal_values)

        if is_current:
            setting = avg_normal * 1.2
        else:
            setting = avg_normal * 0.9

        return setting

    def detect_fault(self, rms_values, setting, is_current=True):

        if not rms_values or setting <= 0:
            return (None, None)

        fault_start = None
        fault_end = None

        for sample_num, value in rms_values:
            if is_current:
                is_fault = value > setting
            else:
                is_fault = value < setting

            if is_fault:
                if fault_start is None:
                    fault_start = sample_num
                fault_end = sample_num

        return (fault_start, fault_end)

    def sample_to_time(self, sample_number):
        """
        Преобразование номера выборки во время в миллисекундах.
        """
        if self.sampling_rate <= 0:
            return 0.0

        time_us = sample_number * (1_000_000 / self.sampling_rate)
        return time_us / 1000.0

    def analyze(self):
        """
        Полный анализ осциллограммы для определения времени начала и окончания КЗ.
        """
        result = {
            'oscillogram_id': self.oscillogram_id,
            'has_current': self.has_current,
            'has_voltage': self.has_voltage,
            'setting_type': None,
            'setting_value': 0.0,
            'fault_start_sample': None,
            'fault_end_sample': None,
            'fault_start_ms': None,
            'fault_end_ms': None,
            'fault_duration_ms': None,
            'channels_analyzed': []
        }

        if self.has_voltage and self.has_current:
            result['setting_type'] = 'impedance'
            all_voltage_rms = []
            all_current_rms = []

            for ch_idx in self.voltage_channels:
                if ch_idx in self.samples_data:
                    rms = self.calculate_rms_sliding(
                        self.samples_data[ch_idx],
                        self.samples_per_cycle
                    )
                    all_voltage_rms.extend(rms)
                    result['channels_analyzed'].append(f'U_{ch_idx}')

            for ch_idx in self.current_channels:
                if ch_idx in self.samples_data:
                    rms = self.calculate_rms_sliding(
                        self.samples_data[ch_idx],
                        self.samples_per_cycle
                    )
                    all_current_rms.extend(rms)
                    result['channels_analyzed'].append(f'I_{ch_idx}')

            voltage_by_sample = {}
            current_by_sample = {}

            for sample_num, rms in all_voltage_rms:
                if sample_num not in voltage_by_sample:
                    voltage_by_sample[sample_num] = []
                voltage_by_sample[sample_num].append(rms)

            for sample_num, rms in all_current_rms:
                if sample_num not in current_by_sample:
                    current_by_sample[sample_num] = []
                current_by_sample[sample_num].append(rms)

            avg_voltage_rms = [
                (sample_num, sum(values) / len(values))
                for sample_num, values in voltage_by_sample.items()
            ]
            avg_current_rms = [
                (sample_num, sum(values) / len(values))
                for sample_num, values in current_by_sample.items()
            ]

            impedance = self.calculate_impedance(avg_voltage_rms, avg_current_rms)

            if impedance:
                setting = self.calculate_setting(impedance, is_current=False)
                result['setting_value'] = setting

                print(f"Уставка по сопротивлению: {setting:.4f} Ом")
                print(f"  (нормальное значение * 0.9)")

                fault_start, fault_end = self.detect_fault(impedance, setting, is_current=False)

                result['fault_start_sample'] = fault_start
                result['fault_end_sample'] = fault_end

                if fault_start is not None:
                    result['fault_start_ms'] = self.sample_to_time(fault_start)
                if fault_end is not None:
                    result['fault_end_ms'] = self.sample_to_time(fault_end)
                if result['fault_start_ms'] is not None and result['fault_end_ms'] is not None:
                    result['fault_duration_ms'] = result['fault_end_ms'] - result['fault_start_ms']

        elif self.has_current:
            result['setting_type'] = 'current'
            print("\nРасчет уставки по току")

            all_current_rms = []

            for ch_idx in self.current_channels:
                if ch_idx in self.samples_data:
                    rms = self.calculate_rms_sliding(
                        self.samples_data[ch_idx],
                        self.samples_per_cycle
                    )
                    all_current_rms.extend(rms)
                    result['channels_analyzed'].append(f'I_{ch_idx}')

            current_by_sample = {}
            for sample_num, rms in all_current_rms:
                if sample_num not in current_by_sample:
                    current_by_sample[sample_num] = []
                current_by_sample[sample_num].append(rms)

            avg_current_rms = [
                (sample_num, sum(values) / len(values))
                for sample_num, values in current_by_sample.items()
            ]

            if avg_current_rms:
                setting = self.calculate_setting(avg_current_rms, is_current=True)
                result['setting_value'] = setting

                print(f"Уставка по току: {setting:.4f} А")
                print(f"  (нормальное значение * 1.2)")

                fault_start, fault_end = self.detect_fault(avg_current_rms, setting, is_current=True)

                result['fault_start_sample'] = fault_start
                result['fault_end_sample'] = fault_end

                if fault_start is not None:
                    result['fault_start_ms'] = self.sample_to_time(fault_start)
                if fault_end is not None:
                    result['fault_end_ms'] = self.sample_to_time(fault_end)
                if result['fault_start_ms'] is not None and result['fault_end_ms'] is not None:
                    result['fault_duration_ms'] = result['fault_end_ms'] - result['fault_start_ms']

        return result

    def print_results(self, results):
        print(f"Осциллограмма ID {results['oscillogram_id']}")
        print(f"\nТип уставки: {results['setting_type']}")
        print(f"Значение уставки: {results['setting_value']:.4f}")
        print(f"Анализированные каналы: {', '.join(results['channels_analyzed'])}")

        if results['fault_start_sample'] is not None:
            print(f"\nОбнаружено КЗ")
            print(f"Начало КЗ:")
            print(f"    Номер выборки: {results['fault_start_sample']}")
            print(f"    Время: {results['fault_start_ms']:.3f} мс")

            if results['fault_end_sample'] is not None:
                print(f"Окончание КЗ:")
                print(f"    Номер выборки: {results['fault_end_sample']}")
                print(f"    Время: {results['fault_end_ms']:.3f} мс")
                print(f"Длительность КЗ: {results['fault_duration_ms']:.3f} мс")
        else:
            print(f"\nКороткое замыкание НЕ обнаружено")