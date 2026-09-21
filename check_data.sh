#!/bin/bash
count=0
while true
do
  new_count=`mysql clg -N -e "select count(sample_id) from xbarb_primary_result"`
  echo "$new_count"
  if [[ "$count" -ne "$new_count" ]]
  then
    data=`mysql clg -E -e "select * from xbarb_primary_result order by sample_id desc limit 1"`
    echo $data
    curl -d "$data"  http://117.217.126.159:4500/xbarb
    count=$new_count
  fi
  sleep 60
done
