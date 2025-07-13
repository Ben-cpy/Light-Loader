#!/bin/bash

# 遍历当前目录下的所有子目录
for dir in */; do
  dir_name=$(basename "$dir")

  # 排除指定目录
  if [[ "$dir_name" == "info" || "$dir_name" == "_yaml" || "$dir_name" == "__pycache__" || "$dir_name" == "template" ]]; then
    continue
  fi

  # 进入子目录
  cd "$dir"

  # 删除 .log 文件和 call_graph.json 文件
  rm -f *.log call_graph.json

  # 返回上级目录
  cd ..

  # 重命名目录
  new_dir_name="ori-$dir_name"
  mv "$dir_name" "$new_dir_name"

  # 修改对应的 .yml 文件
  yml_file="$dir_name.yml"
  if [ -f "$yml_file" ]; then
    sed -i "6s#$dir_name:#ori-$dir_name:#" "$yml_file"  # 修改第 6 行
    sed -i "8s#./#./ori-#" "$yml_file"
    sed -i "9s#localhost:5000/#localhost:5000/ori-#" "$yml_file"

    # 重命名 .yml 文件
    new_yml_file="ori-$yml_file"
    mv "$yml_file" "$new_yml_file"
  fi
done