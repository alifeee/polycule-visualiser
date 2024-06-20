#!/bin/bash
# cgi script for polycule editor

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# enable for debug
# echo "Content-Type: text/plain"
# echo ""
# echo "$(env)"

log=$SCRIPT_DIR/log

echo "" >> $log
echo "[edit.cgi]" >> $log
date >> $log

declare -A param
while IFS='=' read -r -d '&' key value && [[ -n "$key" ]]; do
    param["$key"]=$value
done <<< "$(cat /dev/stdin)&"

# print all vars in param array
# for key in "${!param[@]}"; do
#   echo "$key: ${param[$key]}" >> $log
# done
echo "addnode: ${param[addnode]}" >> $log
echo "removenode: ${param[removenode]}" >> $log
echo "addedge1: ${param[addedge1]}" >> $log
echo "addedge2: ${param[addedge2]}" >> $log
echo "dcedge1: ${param[dcedge1]}" >> $log
echo "dcedge2: ${param[dcedge2]}" >> $log

# sort edges
sortedadds=$(echo -e "${param[addedge1]}\n${param[addedge2]}" | sort)
sorteddcs=$(echo -e "${param[dcedge1]}\n${param[dcedge2]}" | sort)
param[addedge1]=$(echo "${sortedadds}" | head -n1)
param[addedge2]=$(echo "${sortedadds}" | tail -n1)
param[dcedge1]=$(echo "${sorteddcs}" | head -n1)
param[dcedge2]=$(echo "${sorteddcs}" | tail -n1)

json=$(cat $SCRIPT_DIR/polycule.json)
echo "current json:" >> $log
echo "${json}" | jq -c >> $log

if [ ! -z "${param[addnode]}" ]; then
  echo "add node!: ${param[addnode]}" >> $log
  json=$(echo "${json}" | jq '.nodes |= .+ ["'"${param[addnode]}"'"]')
fi
if [ ! -z "${param[removenode]}" ]; then
  echo "remove node!: ${param[removenode]}" >> $log
  appearsinedges=$(echo "${json}" | jq -r '.edges | .[] | .[]' | grep "${param[removenode]}" | wc -l)
  if [ $appearsinedges == 0 ]; then
    json=$(echo "${json}" | jq '.nodes |= .- ["'"${param[removenode]}"'"]')
  else
    echo "refusing to remove node with edges" >> $log
  fi
fi
if [ ! -z "${param[addedge1]}" ] && [ ! -z "${param[addedge2]}" ]; then
  echo "add edge from ${param[addedge1]} to ${param[addedge2]}" >> $log
  edge1innodes=$(echo "${json}" | jq -r '.nodes | .[]' | grep "^${param[addedge1]}$" | wc -l)
  edge2innodes=$(echo "${json}" | jq -r '.nodes | .[]' | grep "^${param[addedge2]}$" | wc -l)
  if [ $edge1innodes != 1 ] || [ $edge2innodes != 1 ]; then
    echo "desired edge not found in edges" >> $log
  elif [ "${param[addedge1]}" == "${param[addedge2]}" ]; then
    echo "desired edges are the same, doing nothing" >> $log
  else
    json=$(echo "${json}" | jq '.edges |= .+ [["'"${param[addedge1]}"'","'"${param[addedge2]}"'"]]')
  fi
fi
if [ ! -z "${param[dcedge1]}" ] && [ ! -z "${param[dcedge2]}" ]; then
  echo "disconnect edge from ${param[dcedge1]} to ${param[dcedge2]}" >> $log
  json=$(echo "${json}" | jq '.edges |= .- [["'"${param[dcedge1]}"'","'"${param[dcedge2]}"'"]]')
fi

echo "json after:" >> $log
echo "${json}" | jq -c >> $log
echo "${json}" > $SCRIPT_DIR/polycule.json
echo "rebuilding site..." >> $log
echo "cannot rebuild site... not able to use npm... copying json manually" >> $log
# (2>&1; cd $SCRIPT_DIR; npm run build >> $log)
cp $SCRIPT_DIR/polycule.json $SCRIPT_DIR/_site/polycule.json

echo "issuing redirect..." >> $log
echo "HTTP/1.1 303 See Other"
echo "Location: /polycule/"
echo ""
echo ""

