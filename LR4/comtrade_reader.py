import sqlite3 as sq

class ComtradeReader:

    def __init__(self, db_path="comtrade.db"):
        self.db_path = db_path
        self.cfg_data = {}
        self.channels = []
        self.samples = []

    def create_tables(self):
        with sq.connect(self.db_path) as con:
            cur = con.cursor()

            # Таблица для хранения информации о файлах осциллограмм
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oscillograms (
                    oscillogram_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    station_name TEXT,
                    version INTEGER,
                    frequency REAL,
                    start_time TEXT,
                    end_time TEXT,
                    data_format TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица для хранения информации о каналах измерения
            cur.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    oscillogram_id INTEGER NOT NULL,
                    channel_index INTEGER NOT NULL,
                    channel_type TEXT NOT NULL,
                    ch_id TEXT,
                    phase TEXT,
                    ccbm TEXT,
                    unit TEXT,
                    coeff_a REAL,
                    coeff_b REAL,
                    skew_us REAL,
                    min_value INTEGER,
                    max_value INTEGER,
                    primary_ratio REAL,
                    secondary_ratio REAL,
                    ps TEXT,
                    normal_state INTEGER,
                    FOREIGN KEY (oscillogram_id) REFERENCES oscillograms(oscillogram_id)
                )
            """)

            # Таблица для хранения выборок данных
            cur.execute("""
                CREATE TABLE IF NOT EXISTS samples (
                    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    oscillogram_id INTEGER NOT NULL,
                    sample_number INTEGER NOT NULL,
                    timestamp_us INTEGER NOT NULL,
                    channel_number INTEGER NOT NULL,
                    value REAL NOT NULL,
                    FOREIGN KEY (oscillogram_id) REFERENCES oscillograms(oscillogram_id)
                )
            """)

    # Парсер .cfg файлов
    def parse_cfg_file(self, cfg_path):
        with open(cfg_path) as f:
            lines = f.readlines()

        # Строка 1: название станции, id записывающего устройства, год стандарта
        header_line = lines[0].strip().split(',')
        self.cfg_data['station_name'] = header_line[0]
        self.cfg_data['rec_id'] = int(header_line[1])
        self.cfg_data['version'] = int(header_line[2])

        # Строка 2: количество каналов (всего, аналоговых, дискретных)
        channel_counts = lines[1].strip().split(',')
        self.cfg_data['total_channels'] = int(channel_counts[0])
        self.cfg_data['analog_channels'] = int(channel_counts[1].replace('A', ''))
        self.cfg_data['digital_channels'] = int(channel_counts[2].replace('D', ''))

        # Парсинг описаний каналов
        self.channels = []
        line_idx = 2

        # Аналоговые каналы
        for i in range(self.cfg_data['analog_channels']):
            parts = lines[line_idx].strip().split(',')
            channel = {
                'channel_index': int(parts[0]),
                'channel_type': 'A',
                'ch_id': parts[1] if len(parts[1]) > 0 else "",
                'phase': parts[2] if len(parts[2]) > 0 else "",
                'ccbm': parts[3] if len(parts[3]) > 0 else "",
                'unit': parts[4] if len(parts[4]) > 0 else "",
                'coeff_a': float(parts[5]) if len(parts[5]) > 0 else 0.0,
                'coeff_b': float(parts[6]) if len(parts[6]) > 0 else 0.0,
                'skew_us': float(parts[7]) if len(parts[7]) > 0 else 0.0,
                'min_value': int(float(parts[8])) if len(parts[8]) > 0 else 0.0,
                'max_value': int(float(parts[9])) if len(parts[9]) > 0 else 0.0,
                'primary_ratio': float(parts[10]) if len(parts[10]) > 0 else 1.0,
                'secondary_ratio': float(parts[11]) if len(parts[11]) > 0 else 1.0,
                'ps': parts[12] if len(parts[12]) > 0 else ""
            }
            self.channels.append(channel)
            line_idx += 1

        # Дискретные каналы
        for i in range(self.cfg_data['digital_channels']):
            parts = lines[line_idx].strip().split(',')
            channel = {
                'channel_index': int(parts[0]),
                'channel_type': 'D',
                'ch_id': parts[1] if len(parts[1]) > 0 else "",
                'phase': parts[2] if len(parts[2]) > 0 else "",
                'ccbm': parts[3] if len(parts[3]) > 0 else "",
                'normal_state': int(parts[4]) if len(parts[4]) > 0 else 0,
                'unit': '',
                'coeff_a': 1.0,
                'coeff_b': 0.0,
                'skew_us': 0.0,
                'min_value': 0,
                'max_value': 1,
                'primary_ratio': 1.0,
                'secondary_ratio': 1.0,
                'ps': ''
            }
            self.channels.append(channel)
            line_idx += 1

        # Частота сети
        self.cfg_data['frequency'] = float(lines[line_idx].strip())
        line_idx += 1

        # Номер схемы
        self.cfg_data['scheme_id'] = int(lines[line_idx].strip())
        line_idx += 1

        # Частота дискретизации и количество выборок
        rate_line = lines[line_idx].strip().split(',')
        self.cfg_data['sampling_rate'] = float(rate_line[0])
        self.cfg_data['total_samples'] = int(rate_line[1])
        line_idx += 1

        # Время начала записи
        self.cfg_data['start_time'] = lines[line_idx].strip()
        line_idx += 1

        # Время окончания записи
        self.cfg_data['end_time'] = lines[line_idx].strip()
        line_idx += 1

        # Формат данных
        self.cfg_data['data_format'] = lines[line_idx].strip()
        line_idx += 1

    # Парсер .dat файлов
    def parse_dat_file(self, dat_path):
        self.samples = []

        with open(dat_path) as f:
            for line in f:
                parts = line.strip().split(',')
                sample_number = int(parts[0])
                timestamp_us = int(parts[1])
                for i, channel in enumerate(self.channels):
                    raw_value = int(parts[2 + i]) if 2 + i < len(parts) else 0

                    if channel['channel_type'] == 'A':
                        calibrated_value = raw_value * channel['coeff_a'] + channel['coeff_b']
                    else:
                        calibrated_value = float(raw_value)

                    sample = {
                        'sample_number': sample_number,
                        'timestamp_us': timestamp_us,
                        'channel_index': channel['channel_index'],
                        'value': calibrated_value
                    }
                    self.samples.append(sample)

    # Сохранение распарсенных данных в БД. Возвращает ID сохраненной осциллограммы в БД
    def save_to_database(self, filename):
        with sq.connect(self.db_path) as con:
            cur = con.cursor()
            # Вставка информации об осциллограмме
            cur.execute("""
                INSERT INTO oscillograms (
                    filename, station_name, version, frequency, 
                    start_time, end_time, data_format
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                filename,
                self.cfg_data.get('station_name', ''),
                self.cfg_data.get('version', 1999),
                self.cfg_data.get('frequency', 50.0),
                self.cfg_data.get('start_time', ''),
                self.cfg_data.get('end_time', ''),
                self.cfg_data.get('data_format', 'ASCII')
            ))

            # Получение ID новой строки
            oscillogram_id = cur.lastrowid

            # Вставка информации о каналах
            for channel in self.channels:
                cur.execute("""
                    INSERT INTO channels (
                        oscillogram_id, channel_index, channel_type, ch_id,
                        phase, ccbm, unit, coeff_a, coeff_b, skew_us,
                        min_value, max_value, primary_ratio, secondary_ratio, ps, normal_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    oscillogram_id,
                    channel['channel_index'],
                    channel['channel_type'],
                    channel['ch_id'],
                    channel['phase'],
                    channel['ccbm'],
                    channel['unit'],
                    channel['coeff_a'],
                    channel['coeff_b'],
                    channel['skew_us'],
                    channel['min_value'],
                    channel['max_value'],
                    channel['primary_ratio'],
                    channel['secondary_ratio'],
                    channel['ps'],
                    channel.get('normal_state', None)
                ))

            # Добавление нескольких записей
            if self.samples:
                sample_data = [(oscillogram_id, s['sample_number'], s['timestamp_us'], s['channel_index'], s['value'])
                               for s in self.samples]
                cur.executemany("""
                    INSERT INTO samples (
                        oscillogram_id, sample_number, timestamp_us, 
                        channel_number, value
                    ) VALUES (?, ?, ?, ?, ?)
                """, sample_data)

            return oscillogram_id

    def load_from_comtrade(self, file_path):
        # Определение имени файла
        cfg_path = file_path
        dat_path = file_path[:-4] + '.dat'
        filename = file_path[:-4]

        # Создаем таблицы если они не существуют
        self.create_tables()

        self.parse_cfg_file(cfg_path) # Чтение конфигурационного файла
        self.parse_dat_file(dat_path) # Чтение файла данных
        oscillogram_id = self.save_to_database(filename) # Сохранение в базу данных

        print(f"Из файлов {cfg_path} и {dat_path} загружена осциллограмма с ID: {oscillogram_id}")

        return oscillogram_id

    # Чтение данных об осцилограмме из БД
    def get_oscillogram_info(self, oscillogram_id):
        with sq.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT oscillogram_id, filename, station_name, version,
                       frequency, start_time, end_time, data_format
                FROM oscillograms
                WHERE oscillogram_id = ?
            """, (oscillogram_id,))
            row = cur.fetchone()
            if row:
                return {
                    'oscillogram_id': row[0],
                    'filename': row[1],
                    'station_name': row[2],
                    'version': row[3],
                    'frequency': row[4],
                    'start_time': row[5],
                    'end_time': row[6],
                    'data_format': row[7]
                }
            return None

    def get_channels(self, oscillogram_id):
        with sq.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT channel_id, channel_index, channel_type, ch_id,
                       phase, ccbm, unit, coeff_a, coeff_b, skew_us,
                       min_value, max_value, primary_ratio, secondary_ratio, ps, normal_state
                FROM channels
                WHERE oscillogram_id = ?
                ORDER BY channel_index
            """, (oscillogram_id,))

            channels = []
            for row in cur.fetchall():
                channels.append({
                    'channel_id': row[0],
                    'channel_index': row[1],
                    'channel_type': row[2],
                    'ch_id': row[3],
                    'phase': row[4],
                    'ccbm': row[5],
                    'unit': row[6],
                    'coeff_a': row[7],
                    'coeff_b': row[8],
                    'skew_us': row[9],
                    'min_value': row[10],
                    'max_value': row[11],
                    'primary_ratio': row[12],
                    'secondary_ratio': row[13],
                    'ps': row[14],
                    'normal_state': row[15]
                })
            return channels

    def get_samples(self, oscillogram_id, channel_index=None):

        query = """
            SELECT sample_id, sample_number, timestamp_us, 
                   channel_number, value
            FROM samples
            WHERE oscillogram_id = ?
        """
        params = [oscillogram_id]

        if channel_index is not None:
            query += " AND channel_number = ?"
            params.append(channel_index)

        query += " ORDER BY sample_number, channel_number"

        with sq.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(query, params)

            samples = []
            for row in cur.fetchall():
                samples.append({
                    'sample_id': row[0],
                    'sample_number': row[1],
                    'timestamp_us': row[2],
                    'channel_index': row[3],
                    'value': row[4]
                })
            return samples
