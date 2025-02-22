# PDF转换平台UI设计规范

## 1. 设计理念

### 1.1 设计原则
- **简洁性**：界面清晰，操作直观
- **专业性**：体现专业工具属性
- **可用性**：降低学习成本
- **一致性**：统一的设计语言

### 1.2 品牌基调
- **现代商务风格**
- **科技感与人文关怀的结合**
- **注重细节和用户体验**
- **专业可靠的形象**

## 2. 色彩系统

### 2.1 主色调
```css
--primary: #2563EB;     /* 主题蓝 */
--primary-light: #60A5FA;  /* 浅蓝 */
--primary-dark: #1E40AF;   /* 深蓝 */
```

### 2.2 辅助色
```css
--success: #10B981;     /* 成功绿 */
--warning: #F59E0B;     /* 警告黄 */
--danger: #EF4444;      /* 错误红 */
--info: #6B7280;        /* 信息灰 */
```

### 2.3 中性色
```css
--text-primary: #1F2937;   /* 主要文字 */
--text-secondary: #4B5563; /* 次要文字 */
--text-disabled: #9CA3AF;  /* 禁用文字 */
--border: #E5E7EB;         /* 边框 */
--background: #F3F4F6;     /* 背景 */
--white: #FFFFFF;          /* 纯白 */
```

## 3. 字体规范

### 3.1 字体家族
```css
/* 中文 */
font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;

/* 英文 */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
```

### 3.2 字号规范
```css
--font-xs: 12px;    /* 辅助文字 */
--font-sm: 14px;    /* 正文（小） */
--font-base: 16px;  /* 正文 */
--font-lg: 18px;    /* 小标题 */
--font-xl: 20px;    /* 标题 */
--font-2xl: 24px;   /* 大标题 */
--font-3xl: 30px;   /* 主标题 */
```

### 3.3 行高
```css
--leading-none: 1;      /* 无 */
--leading-tight: 1.25;  /* 紧凑 */
--leading-normal: 1.5;  /* 正常 */
--leading-loose: 1.75;  /* 宽松 */
```

## 4. 间距规范

### 4.1 内边距（Padding）
```css
--padding-xs: 4px;
--padding-sm: 8px;
--padding-md: 16px;
--padding-lg: 24px;
--padding-xl: 32px;
```

### 4.2 外边距（Margin）
```css
--margin-xs: 4px;
--margin-sm: 8px;
--margin-md: 16px;
--margin-lg: 24px;
--margin-xl: 32px;
```

### 4.3 间隔（Gap）
```css
--gap-xs: 4px;
--gap-sm: 8px;
--gap-md: 16px;
--gap-lg: 24px;
--gap-xl: 32px;
```

## 5. 组件规范

### 5.1 按钮
1. **主要按钮**
```css
background: var(--primary);
color: var(--white);
padding: 12px 24px;
border-radius: 8px;
font-weight: 500;
```

2. **次要按钮**
```css
background: var(--white);
color: var(--primary);
border: 1px solid var(--primary);
padding: 12px 24px;
border-radius: 8px;
```

3. **文字按钮**
```css
color: var(--primary);
background: transparent;
padding: 12px 24px;
```

### 5.2 输入框
```css
border: 1px solid var(--border);
border-radius: 8px;
padding: 12px 16px;
background: var(--white);
```

### 5.3 卡片
```css
background: var(--white);
border-radius: 12px;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
padding: var(--padding-lg);
```

## 6. 响应式断点

### 6.1 断点定义
```css
--screen-sm: 640px;   /* 手机 */
--screen-md: 768px;   /* 平板 */
--screen-lg: 1024px;  /* 小桌面 */
--screen-xl: 1280px;  /* 大桌面 */
--screen-2xl: 1536px; /* 超大屏 */
```

### 6.2 容器宽度
```css
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
```

## 7. 动画效果

### 7.1 过渡时间
```css
--duration-75: 75ms;
--duration-100: 100ms;
--duration-150: 150ms;
--duration-200: 200ms;
--duration-300: 300ms;
```

### 7.2 过渡曲线
```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

## 8. 图标规范

### 8.1 图标尺寸
```css
--icon-xs: 16px;
--icon-sm: 20px;
--icon-md: 24px;
--icon-lg: 32px;
--icon-xl: 40px;
```

### 8.2 图标颜色
- 继承文字颜色
- 使用当前色值（currentColor）
- 保持图标风格统一

## 9. 阴影效果

### 9.1 阴影定义
```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
--shadow-xl: 0 20px 25px rgba(0,0,0,0.1);
```

## 10. 响应式设计

### 10.1 布局网格
- 使用12列栅格系统
- 响应式间距调整
- 弹性盒模型布局
- CSS Grid布局

### 10.2 图片处理
- 响应式图片
- 懒加载
- WebP格式支持
- 图片占位符

## 11. 交互状态

### 11.1 悬停状态
```css
--hover-opacity: 0.8;
--hover-scale: 1.02;
--hover-shadow: var(--shadow-md);
```

### 11.2 激活状态
```css
--active-opacity: 0.7;
--active-scale: 0.98;
```

### 11.3 禁用状态
```css
--disabled-opacity: 0.5;
--disabled-bg: var(--background);
```

## 12. 主题定制

### 12.1 亮色主题
```css
--theme-bg: var(--white);
--theme-text: var(--text-primary);
--theme-border: var(--border);
```

### 12.2 暗色主题
```css
--theme-bg-dark: #1F2937;
--theme-text-dark: #F9FAFB;
--theme-border-dark: #374151;
``` 