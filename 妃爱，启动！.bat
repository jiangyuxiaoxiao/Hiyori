if not exist .\venv\ (
    pip install virtualenv
    virtualenv venv
    call venv\Scripts\activate
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    cd .\Hiyori
    python hiyori.py
    pause
) else (
    call venv\Scripts\activate
    cd .\Hiyori
    python hiyori.py
    pause
)