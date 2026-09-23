#!/bin/bash
previous_id=`cat /root/pbrtqc/last_sample_id_NXL_1000`
new_id=`mysql clg -N -e "select sample_id from xbarb_primary_result where uniq='NXL_1000|xbarb' order by sample_id desc limit 1"`
echo $previous_id
echo $new_id
if [ $previous_id -ne $new_id ]
then
	data=`mysql clg -E -e "select sample_id,round(result,2),uniq from xbarb_primary_result where uniq='NXL_1000|xbarb' and sample_id=$new_id"|tail -3`
	echo $data
	curl -d "$data"  http://117.217.126.159:4500/xbarb
	echo $new_id > /root/pbrtqc/last_sample_id_NXL_1000
#else
        #curl -d "No new data for NXL_1000"  http://117.217.126.159:4500/xbarb
fi
