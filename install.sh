if hash virtualenv; then
  virtualenv venv 2>/dev/null
else
  echo 'no virtualenv'
  if hash pip 2>/dev/null; then
    pip install virtualenv
    virtualenv venv 2>/dev/null
  else
    echo >&2 "Pip is not installed. Aborting."; exit 1;
  fi

fi

source venv/bin/activate
pip install -r requirements.txt
