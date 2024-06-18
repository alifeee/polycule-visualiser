#!/bin/bash
# cgi script for polycule editor

echo "Content-type: text/plain"
echo ""

declare -A param
while IFS='=' read -r -d '&' key value && [[ -n "$key" ]]; do
    param["$key"]=$value
done <<< "$(cat /dev/stdin)&"

# print all vars in param array
# for key in "${!param[@]}"; do
#   echo "$key: ${param[$key]}"
# done

if [ ! -z "${param[addnode]}" ]; then
  echo "add node!: ${param[addnode]}"
fi
if [ ! -z "${param[removenode]}" ]; then
  echo "remove node!: ${param[removenode]}"
fi
if [ ! -z "${param[addedge1]}" ] && [ ! -z "${param[addedge2]}" ]; then
  echo "add edge from ${param[addedge1]} to ${param[addedge2]}"
fi
if [ ! -z "${param[dcedge1]}" ] && [ ! -z "${param[dcedge2]}" ]; then
  echo "disconnect edge from ${param[dcedge1]} to ${param[dcedge2]}"
fi
