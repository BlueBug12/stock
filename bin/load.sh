if [ "$#" -eq 0 ]
then
  targets=( '2330' '0050' '2303' '2449' '2886' '3008' '1301' '2308' '2344' '2454' '2891' '3034' '1444' '2603' '2449' '2353' '2368')
  for stock in "${targets[@]}"
  do
    python3 loader.py "$stock"
  done
else
  for var in "$@"
  do
    python3 loader.py "$var"
  done
fi

