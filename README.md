
###Information Flow:
- run calculate_ma.py
- xbarb_xxx_lab_reference_value is searched for currently valid algorithm data
- last entry (containing last sample_id used for calculation) from xbarb_primary_result is found for each valid algorithm
- new batch of bin_size is found from primary_result
- xbarb / other alogrithm are run
- result entered in xbarb_primary_result (if number of results are at least bin_size)
- run the script using crontab to check at repeat intervals

###Tables used
```
CREATE TABLE `primary_result` (
  `sample_id` bigint(20) NOT NULL,
  `examination_id` int(11) NOT NULL,
  `result` varchar(5000) NOT NULL,
  `extra` varchar(5000) DEFAULT NULL,
  `uniq` varchar(100) NOT NULL,
  PRIMARY KEY (`sample_id`,`examination_id`,`uniq`),
) 


CREATE TABLE `xbarb_primary_result` (
  `sample_id` bigint(20) NOT NULL,
  `examination_id` int(11) NOT NULL,
  `result` varchar(5000) NOT NULL,
  `extra` varchar(5000) DEFAULT NULL,
  `uniq` varchar(100) NOT NULL,
  PRIMARY KEY (`sample_id`,`examination_id`,`uniq`),
) 

CREATE TABLE `xbarb_xxx_lab_reference_value` (
  `lab_reference_value_id` int(11) NOT NULL AUTO_INCREMENT,
  `bin_size` varchar(100) NOT NULL,
  `examination_id` int(11) NOT NULL,
  `algorithm` varchar(100) NOT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `mean` decimal(10,2) NOT NULL,
  `sd` decimal(10,2) NOT NULL,
  `manufacturer_data` varchar(100) DEFAULT NULL,
  `remark` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`lab_reference_value_id`),
) 
```
