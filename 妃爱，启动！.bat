if not exist .\venv\ (
    pip install virtualenv
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)
call venv\Scripts\activate
cd .\Hiyori
python hiyori.py
pause