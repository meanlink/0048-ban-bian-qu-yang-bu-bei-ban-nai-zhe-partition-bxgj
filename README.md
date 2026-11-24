# 板边取样簿 · 背板耐折分区

样木相框社的 6 位小批量装裱工在裁切前检验纤维背板。供料人员按整板划出取样区，检测工登记夹具和挠度，裁切桌收到签发单。以往在货签、夹具表和共享试验表抄结果，容易把板边和中部混算、无法追溯夹具零位、复测时覆盖原检测卡。

| 角色 | 动作 |
|---|---|
| operator | 登记靠边带与中腹区取样、录入夹具测量 |
| reviewer | 排除取样夹持错误的原卡，判断复测后能否签发 |
| viewer | 读整板图、检测卡、分布及裁切签发 |

1. 11 月 19 日 08:20 根据《FLEX-17_result.csv》检查 3 mm 批次各区 3 片。
2. 08:40 JIG-4 使用 150 mm 检测跨距，零位 0.20 mm。
3. 09:00 S-13 靠边样实读 4.60 mm，零位校正后的挠度为 4.40 mm。
4. 10:00 分区图显示靠边带 P90 为 3.96 mm，超出 2.90 mm 限制。
5. 11:30 复核发现样片压线偏移，排除原检测卡，留下依据。
6. 13:00 同件样片重新测量 2.60 mm，标准化值 2.40 mm，靠边带 P90 为 2.36 mm。
7. 14:15 复核员签发面框内宽 220 mm 的裁切单，worker 生成简版批签凭据。

算法按区取有效卡的零位校正结果，分别计算中位数、相对中位数的绝对偏差中位数 MAD 以及 P90 的线性分位插值。两区至少各 3 个有效样片，所有已登记取样均须有有效卡。夹具过校期或厚度不适配的测量拒绝接纳；复测需先有排除说明。

```sh
cp -n .env.example .env
docker compose up -d --build --wait
docker compose exec backend python -m scripts.seed_demo
docker compose down -v --remove-orphans
```

三个演示账号为 operator@demo.local、reviewer@demo.local、viewer@demo.local，默认密码 Demo2026!。FRONTEND_PORT、BACKEND_PORT、DB_PORT 决定宿主端口，SEED_DEMO 控制自动填充，JWT_SECRET、DEMO_PASSWORD、POSTGRES_PASSWORD 可改为自己的配置。五服务使用 Nginx 原生 ES modules、FastAPI、Python worker、Redis 和 PostgreSQL。后端本地开发安装 backend/requirements.txt，配置 DATABASE_URL、REDIS_URL、JWT_SECRET，然后运行 `uvicorn app:app --reload` 和 `python worker.py`。backend/frame 为分区、夹具、检测与签单逻辑，frontend/caliper 为工台。角色和任务枚举在 backend/core.py 与 frontend/base.js；取样区与检测状态在 schema.sql、backend/frame/request.py、inspection.py 和 frontend/caliper/lexicon.js。MIT 许可证。

前端地址为 http://127.0.0.1:18442，API 为 http://127.0.0.1:19442，数据库本机映射端口为 17942。
