# CF IP DNS

**项目源自：** [ZhiXuanWang/cf-speed-dns](https://github.com/ZhiXuanWang/cf-speed-dns)

**CF优选IP，实时更新列表页面：** [CF优选IP列表](https://ip.164746.xyz)

**CF优选IP接口：** [CF优选IP接口](https://ip.164746.xyz/ipTop.html)

## GitHub Actions 配置

要配置 GitHub Actions 以自动运行此项目，请按照以下步骤操作：

1. **添加 GitHub Secrets**：
   1. 进入你的 GitHub 仓库。
   2. 点击 **Settings**（设置）。
   3. 在左侧菜单中找到 **Secrets and variables** > **Actions**。
   4. 点击 **New repository secret**（新建仓库密钥）。
   5. 添加以下密钥：
      - `CF_API_TOKEN`：你的 Cloudflare API 令牌（例如：`xxxxx`）
      - `CF_ZONE_ID`：你的 Cloudflare 区域 ID（例如：`xxxxx`）
      - `CF_DNS_NAME`：要更新的 DNS 名称（例如：`dns.abc.com`）

2. **配置 GitHub Actions 工作流程**：
   - 在你的仓库中创建 `.github/workflows/run_dnscf.yml` 文件

完成这些步骤后，GitHub Actions 将根据你设置的计划任务自动运行，并更新你的 Cloudflare DNS 记录。
