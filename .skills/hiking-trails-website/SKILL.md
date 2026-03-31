# 徒步路线展示网站构建技能

## 技能描述
创建一个功能完整的徒步路线展示网站，包含地图展示、路线搜索、详情查看等核心功能。

## 技术栈
- HTML5 - 语义化页面结构
- CSS3 - 现代化UI设计，响应式布局
- JavaScript (ES6+) -交互逻辑
- Leaflet.js - 开源地图库
- OpenStreetMap - 地图数据源
- Font Awesome - 图标库

## 创建步骤

### 1. 创建主HTML文件 (index.html)
- 导航栏（固定顶部）
- 英雄区域（大图背景+搜索框）
- 统计数据横幅
- 路线卡片网格
- 交互式地图区域
- 徒步贴士区域
- 页脚
- 路线详情模态框

### 2. 创建样式文件 (styles.css)
- 定义CSS变量主题颜色
- 实现响应式Grid布局
- 卡片悬停动画效果
- 模态框样式和动画
- 媒体查询适配移动端

### 3. 创建数据文件 (trails-data.js)
定义徒步路线数据结构：
```javascript
{
    id: 数字,
    name: "路线名称",
    difficulty: "easy/moderate/hard",
    distance: 数字(公里),
    duration: "时长",
    elevation: 数字(米),
    rating: 数字(0-5),
    reviews: 数字,
    image: "图片URL",
    description: "描述",
    features: ["特色1", "特色2"],
    start: "起点",
    end: "终点",
    season: "最佳季节",
    transport: "交通方式",
    coords: [纬度, 经度],
    trailPath: [[纬度, 经度], ...]  // 可选
}
```

### 4. 创建主脚本文件 (script.js)
核心功能实现：
- `initMap()` - 初始化Leaflet地图
- `renderTrails(filter)` - 渲染路线卡片
- `addTrailMarkers()` - 添加地图标记
- `viewTrailDetails(id)` - 显示路线详情
- `searchTrails()` - 搜索功能
- `animateStats()` - 数字动画
- `initSmoothScroll()` - 平滑滚动

### 5. 创建配置文件 (config-guide.js)
提供可配置项：
- 网站名称和主题颜色
- 地图默认中心和缩放
- 难度等级规则
- 路线分类标签
- 辅助函数

### 6. 创建文档 (README.md)
- 项目介绍
- 快速开始指南
- 自定义数据说明
- 功能特性列表

## 关键特性

### 地图功能
- 使用Leaflet.js创建交互式地图
- 不同颜色标记表示不同难度
- 绘制路线轨迹线
- 点击标记显示信息弹窗

### 搜索筛选
- 按路线名称搜索
- 按难度等级筛选（简单/中等/困难）
- 实时过滤结果

### 响应式设计
- 桌面端：Grid多列布局
- 平板端：双列布局
- 移动端：单列布局 + 汉堡菜单

### 用户体验
- 路线卡片悬停动画
- 详情模态框（含迷你地图）
- Toast提示消息
- 统计数字滚动动画
- 平滑滚动导航

## 文件结构
```
project/
├── index.html      # 主页面
├── styles.css      # 样式
├── script.js       # 主逻辑
├── trails-data.js  # 路线数据
└── README.md       # 文档
```

## 自定义贴士

### 添加新路线
1. 编辑 `trails-data.js`
2. 复制现有路线对象
3. 修改ID和信息
4. 更新coords坐标

### 修改主题色
在 `styles.css` 的 `:root` 中修改：
```css
:root {
    --primary-color: #你的颜色;
    --secondary-color: #你的颜色;
}
```

### 更改地图位置
在 `script.js` 的 `initMap()` 中：
```javascript
map.setView([纬度, 经度], 缩放级别);
```

## 注意事项

1. **图片资源**：示例使用Unsplash图片，生产环境替换为本地图片
2. **坐标格式**：使用WGS84坐标系 [纬度, 经度]
3. **浏览器兼容**：支持现代浏览器（Chrome/FF/Safari/Edge）
4. **CDN依赖**：确保网络可访问Leaflet和OpenStreetMap

## 扩展建议

- 添加用户登录和账户系统
- 集成天气API显示天气信息
- 添加GPS轨迹导入功能
- 实现路线收藏和分享
- 开发移动端APP
- 添加后台管理系统