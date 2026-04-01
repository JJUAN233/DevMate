# 🏔️ 现代徒步网站项目开发规范 (Full-stack Node.js & Map Policy)

本规范定义了 **DevMate** 智能体在构建具备现代开发流的徒步路线项目时必须遵循的技术标准。

## 🛡️ 核心红线 (Strict Isolation & Policy) - 关键
1. **禁止根目录污染**: 所有项目文件必须封装在 `test_output/` 下的专属子目录内。
2. **地图服务政策 (OSM Policy)**: 
   - **推荐图源**: 必须使用更稳定的第三方分发源，如 **CartoDB**。
     - *URL 示例*: `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png`
   - **强制版权声明**: 所有的 Map Layer 必须包含正确的 `attribution` 字符串。

## 🛠️ 技术栈约束 (Node.js Driven Stack)

### 核心环境 - 彻底移除 Python
- **运行方式 (强制)**: 项目必须原生支持 **`npm run dev`**。
- **包管理**: 使用 **npm** (Node.js 20+)。

### 架构模式 - 非纯前端设计
- **非纯静态化**: 要求具备清晰的数据/视图分离逻辑，禁止生成只有单一 HTML 文件的项目。

## 🗺️ 地图深度功能规范 (Leaflet & Advanced Logic)

1. **磁贴图层配置 (TileLayer Fix)**:
   ```javascript
   L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
       attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
       subdomains: 'abcd',
       maxZoom: 20
   }).addTo(map);
   ```
2. **动态轨迹绘制 (Polyline)**: 渲染轨迹并支持路径高亮。
3. **坐标标记**: 绿色起点 + 红色终点。
4. **实时距离计算**: 基于算法自动计算路径总长度。

## 🚀 开发与部署流程

1. **依赖先行**: 引导用户先运行 `npm install`。
2. **热更新热部署**: 确保 `npm run dev` 环境下地图和组件均能正常呈现。

