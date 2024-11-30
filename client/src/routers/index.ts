import { useStore } from '@/store';
import { defineAsyncComponent } from 'vue';
import { createRouter, createWebHistory, useRouter } from 'vue-router'


const router = createRouter({
    history: createWebHistory(),
    routes: [

        {
            path: '/',
            meta: {
                requiresAuth: true
            },
            children: [
                {
                    path: '',
                    name: "index",
                    component: defineAsyncComponent(() => import('@/pages/Index.vue'))
                },
                {
                    path: 'information',
                    name: "information",
                    component: defineAsyncComponent(() => import('@/pages/Information.vue'))
                },
                {
                    path: 'questions',
                    name: "questions",
                    component: defineAsyncComponent(() => import('@/pages/Questions.vue'))
                },
            ]

        },
        { path: '/:pathMatch(.*)*', name: 'NotFound', component: defineAsyncComponent(() => import('@/pages/Index.vue')) },

    ]
})


router.beforeEach((to: any, from: any, next: any) => {
    const store = useStore();
    const route = useRouter();
    store.state.siteLoading = true;
    const platform = (window as any).Telegram.WebApp.platform;
    const initData = (window as any).Telegram.WebApp.initData;

    const { path, name, meta, component } = to;
    
    if (name === "index")
        (window as any).Telegram.WebApp.BackButton.isVisible = false;
    else {
        (window as any).Telegram.WebApp.BackButton.isVisible = true;
        (window as any).Telegram.WebApp.BackButton.onClick(() => route.back())
    }

    // if (meta.requiresAuth && ["android", "ios"].includes(platform.toLowerCase()) == false) {
    //     return router.push({ name: 'exception', params: { status: 0 } });
    // }

    return next()

});
router.afterEach(() => {
    const store = useStore();
    store.state.siteLoading = false;
    (window as any).Telegram.WebApp.expand();
});

export default router