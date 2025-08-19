export default [
  {
    path: '/user',
    layout: false,
    routes: [
      {
        path: '/user',
        routes: [
          {
            name: 'login',
            path: '/user/login',
            component: './user/Login',
          },
          {
            component: './404',
          },
        ],
      },
    ],
  },
  {
    path: '/',
    redirect: '/image/list',
  },
  {
    path: '/image',
    name: '图片管理',
    icon: 'DatabaseOutlined',
    routes: [
      {
        name: '图片列表',
        path: '/image/list',
        component: './image/image',
      },
      {
        component: './404',
      },
    ],
  },
  {
    path: '/predict',
    name: '识别体验',
    icon: 'FileSearchOutlined',
    component: './image/predict',
  },
  {
    component: './404',
  },
];
