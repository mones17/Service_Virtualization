/*
Warning: Table servicevirtualization.mytable omitted because it has constructs not compatible with CQL (was created via legacy API).
Approximate structure, for reference:
(this should not be used to reproduce this schema)

CREATE TABLE IF NOT EXISTS servicevirtualization.mytable (
    id int,
    myfield text,
    PRIMARY KEY (id)
) WITH COMPACT STORAGE
    AND ID = 72362800-5efe-11ee-9499-c524dc287d30
    AND CLUSTERING ORDER BY (column1 ASC)
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
*/
