ALTER TABLE weekly_features

ADD COLUMN violent_events INT DEFAULT 0,

ADD COLUMN high_severity_events INT DEFAULT 0,

ADD COLUMN remote_explosives_ied INT DEFAULT 0,

ADD COLUMN air_drone_strikes INT DEFAULT 0,

ADD COLUMN suicide_bombs INT DEFAULT 0,

ADD COLUMN mob_violence INT DEFAULT 0,

ADD COLUMN violent_demonstrations INT DEFAULT 0,

ADD COLUMN total_events_lag_3 FLOAT NULL,

ADD COLUMN total_events_lag_4 FLOAT NULL,

ADD COLUMN fatalities_lag_3 FLOAT NULL,

ADD COLUMN fatalities_lag_4 FLOAT NULL,

ADD COLUMN violent_events_lag_1 FLOAT NULL,

ADD COLUMN violent_events_lag_2 FLOAT NULL,

ADD COLUMN violent_events_lag_3 FLOAT NULL,

ADD COLUMN violent_events_lag_4 FLOAT NULL,

ADD COLUMN high_severity_events_lag_1 FLOAT NULL,

ADD COLUMN high_severity_events_lag_2 FLOAT NULL,

ADD COLUMN high_severity_events_lag_3 FLOAT NULL,

ADD COLUMN high_severity_events_lag_4 FLOAT NULL,

ADD COLUMN abductions_lag_1 FLOAT NULL,

ADD COLUMN abductions_lag_2 FLOAT NULL,

ADD COLUMN abductions_lag_3 FLOAT NULL,

ADD COLUMN abductions_lag_4 FLOAT NULL,

ADD COLUMN total_events_4wk_sum FLOAT NULL,

ADD COLUMN total_fatalities_4wk_sum FLOAT NULL,

ADD COLUMN violent_events_4wk_mean FLOAT NULL,

ADD COLUMN violent_events_4wk_sum FLOAT NULL,

ADD COLUMN high_severity_events_4wk_mean FLOAT NULL,

ADD COLUMN high_severity_events_4wk_sum FLOAT NULL,

ADD COLUMN violent_event_change_1wk FLOAT NULL,

ADD COLUMN high_severity_change_1wk FLOAT NULL,

ADD COLUMN abduction_change_1wk FLOAT NULL,

ADD COLUMN event_pct_change_1wk FLOAT NULL,

ADD COLUMN fatality_pct_change_1wk FLOAT NULL,

ADD COLUMN violent_event_ratio FLOAT NULL,

ADD COLUMN high_severity_ratio FLOAT NULL,

ADD COLUMN battle_ratio FLOAT NULL,

ADD COLUMN civilian_violence_ratio FLOAT NULL,

ADD COLUMN abduction_ratio FLOAT NULL,

ADD COLUMN explosion_ratio FLOAT NULL,

ADD COLUMN protest_ratio FLOAT NULL,

ADD COLUMN events_increasing TINYINT DEFAULT 0,

ADD COLUMN fatalities_increasing TINYINT DEFAULT 0,

ADD COLUMN violence_increasing TINYINT DEFAULT 0,

ADD COLUMN high_severity_increasing TINYINT DEFAULT 0,

ADD COLUMN year INT NULL,

ADD COLUMN month INT NULL,

ADD COLUMN quarter INT NULL,

ADD COLUMN week_of_year INT NULL;