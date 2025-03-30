cd $(dirname $0)
mkdir -p dist
cd src/web/app

zip -r ../../../dist/web-src.zip . -x "test/**" "__pycache__/**" "instance/**" ".gitignore"