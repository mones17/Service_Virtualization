CREATE TABLE IF NOT EXISTS servicevirtualization.response (
    id uuid PRIMARY KEY,
    comment text,
    date_created timestamp,
    headers text,
    is_valid boolean,
    last_access timestamp,
    last_update timestamp,
    payload text,
    request_id text,
    request_payload text,
    status_code text,
    time_taken int
) WITH ID = 5d443bf0-1d0c-11ee-af6a-fd7a04f9fd47
    AND additional_write_policy = '99p'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND cdc = false
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '16', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND memtable = 'default'
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND extensions = {}
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
