```shell
# 开发前
git checkout dev
git pull origin dev
# 新建自己的分支
git checkout -b 你的开发分支名

#提交
git add .
git commit -m "更改的信息"
git checkout dev
git rebase 你的开发分支名  # 冲突解决
git push origin dev
```

