# Discrete action learning 动画组件

这是从原页面中拆出的可复用 React/Next.js 组件。组件只依赖 React，动画由原生 CSS 和 SVG 实现，无需安装动画库。

## 目录结构

```text
discrete-action-learning-component/
├── react/
│   ├── DiscreteActionLearning.tsx
│   ├── discrete-action-learning.css
│   └── index.ts
├── assets/
│   └── preview.png
└── README.md
```

## 接入 React / Next.js

1. 把 `react` 目录复制到你项目的组件目录，例如 `components/discrete-action-learning/`。
2. 在页面中引入并渲染：

```tsx
import { DiscreteActionLearning } from '@/components/discrete-action-learning';

export default function Page() {
  return <DiscreteActionLearning />;
}
```

`DiscreteActionLearning.tsx` 会自动引入同目录下的 CSS。如果你的构建工具不允许组件直接引入 CSS，则删除组件顶部的 CSS import，并在项目全局入口引入：

```tsx
import '@/components/discrete-action-learning/discrete-action-learning.css';
```

## 替换标题和说明

```tsx
<DiscreteActionLearning
  title="Your title"
  description="Your description"
/>
```

## 调整颜色

在你的项目 CSS 中覆盖以下变量：

```css
.my-action-section {
  --dal-primary: #147b6d;
  --dal-eef: #13806f;
  --dal-hand: #3560bf;
  --dal-lower: #b7652a;
  --dal-background: #f1f1ec;
  --dal-foreground: #17211f;
}
```

```tsx
<DiscreteActionLearning className="my-action-section" />
```

## 注意事项

- 建议将组件放在至少 `720px` 宽的容器中；窄屏下流程图可横向滚动。
- 组件会自动遵循操作系统的“减少动态效果”设置。
- 所有样式使用 `dal-` 前缀，以减少与其他项目的样式冲突。
