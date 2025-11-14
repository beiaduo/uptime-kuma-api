# 上传到 GitHub 后需要修改的文件

上传项目到 GitHub 后，你需要修改以下文件中的占位符。

## 1. 修改 deploy.sh

文件位置: `deploy.sh`

找到第 27 行：
```bash
GITHUB_REPO="CHANGE_ME"  # ⚠️ 请在上传到 GitHub 后修改为你的仓库地址
```

改为：
```bash
GITHUB_REPO="https://github.com/你的用户名/仓库名.git"
```

例如：
```bash
GITHUB_REPO="https://github.com/jason/uptime-kuma-rest-api.git"
```

## 2. 修改 README.md

文件位置: `README.md`

找到所有包含 `YOUR_USERNAME/YOUR_REPO` 的地方（大约有 3 处），替换为你的实际仓库路径。

**第 1 处**（第 20 行）：
```bash
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/master/deploy.sh
```

改为：
```bash
wget https://raw.githubusercontent.com/你的用户名/仓库名/master/deploy.sh
```

**第 2 处**（第 42 行）：
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

改为：
```bash
git clone https://github.com/你的用户名/仓库名.git
```

**第 3 处**（第 43 行）：
```bash
cd YOUR_REPO
```

改为：
```bash
cd 仓库名
```

## 快速替换方法

如果你使用的是 Linux/macOS，可以用以下命令快速替换：

```bash
# 设置你的 GitHub 用户名和仓库名
USERNAME="你的用户名"
REPO="仓库名"

# 替换 deploy.sh
sed -i.bak "s|GITHUB_REPO=\"CHANGE_ME\".*|GITHUB_REPO=\"https://github.com/$USERNAME/$REPO.git\"|" deploy.sh

# 替换 README.md
sed -i.bak "s|YOUR_USERNAME/YOUR_REPO|$USERNAME/$REPO|g" README.md
sed -i.bak "s|YOUR_REPO|$REPO|g" README.md

# 删除备份文件
rm -f deploy.sh.bak README.md.bak

echo "替换完成！"
```

## 示例

假设你的 GitHub 信息是：
- 用户名: `jason`
- 仓库名: `uptime-kuma-rest-api`

那么替换后应该是：

**deploy.sh**:
```bash
GITHUB_REPO="https://github.com/jason/uptime-kuma-rest-api.git"
```

**README.md**:
```bash
wget https://raw.githubusercontent.com/jason/uptime-kuma-rest-api/master/deploy.sh
git clone https://github.com/jason/uptime-kuma-rest-api.git
cd uptime-kuma-rest-api
```

## 完成后

修改完成并提交后，用户就可以使用以下命令一键部署了：

```bash
wget https://raw.githubusercontent.com/你的用户名/仓库名/master/deploy.sh
chmod +x deploy.sh
./deploy.sh
```
