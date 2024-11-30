import { InjectionKey } from 'vue'
import { createStore, useStore as baseUseStore, Store } from 'vuex'
import createPersistedState from "vuex-persistedstate";

export interface State {
    siteLoading: boolean;
}

export const key: InjectionKey<Store<State>> = Symbol()

export const store = createStore<State>({
    state: {
        siteLoading: true,
    },
    mutations: {
       
    },
    getters: {
      
    },
    // plugins: [createPersistedState()]
})

export function useStore() {
    return baseUseStore(key)
}