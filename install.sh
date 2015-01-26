if hash pip 2>/dev/null; then
    pip install -r requirements.txt
else
    echo >&2 "Pip is not installed. Aborting."; exit 1;
fi
