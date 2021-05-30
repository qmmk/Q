#!/bin/bash
usage="Usage: $(basename $0) pid"
case "$*" in
 ''|*[!0-9]*)
  echo "$usage" 1>&2
  exit 1
  ;;
 * )
  pid="$1"
  ;;
esac
read -r -a pinfo <<< $(cat "/proc/$pid/stat" 2>/dev/null)
if (( ${#pinfo[@]} == 0 )) ; then
  echo -e "No proccess with PID : $pid" >&2
  exit 2
fi
let clk_tck="$(getconf CLK_TCK)"
let utime="${pinfo[13]}"
let stime="${pinfo[14]}"
let cputime=(utime + stime)*1000/clk_tck
echo "PID : ${pinfo[0]}
Cmd : ${pinfo[1]}
CPU : $cputime msec"