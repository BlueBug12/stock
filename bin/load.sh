if [ "$#" -eq 0 ]
then
    python3 loader.py 2330
    python3 loader.py 2454
    python3 loader.py 3008
    python3 loader.py 2308
    python3 loader.py 2303
else
  for var in "$@"
  do
    python3 loader.py "$var"
  done
fi

