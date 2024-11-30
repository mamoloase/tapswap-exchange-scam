<template>
  <div v-if="$store.state.siteLoading" class="modal bg-color w-full h-screen flex-center loader-bg">
    <div class="loader"></div>
  </div>

  <div class="w-full h-screen grow-1 d-flex align-items-start justify-content-start flex-column display">
    <header class="w-full flex-center">
      <section class="my-3">
        <div class="flex-center">
          <img src="@/assets/images/logo.png" width="180px" alt="" />
        </div>
      </section>
    </header>
      <KeepAlive>
        <router-view v-slot="{ Component, route }">
            <Transition name="fade" mode="out-in">
              <main :key="route.name"
                class="overflow-scroll grow-1 d-flex align-items-start justify-content-start flex-column w-full h-full container">
                <component :is="Component"></component>
              </main>
            </Transition>
        </router-view>
      </KeepAlive>


    <footer v-if="!$route.meta.hideFooter" class="footer flex-center w-full">
      <div class="d-flex align-items-center justify-content-between gap-2 w-full m-1 overflow-hidden">
        <div @click="$router.push({ name: 'information' })"
          class="flex-center flex-column p-2 gap-2 bg-card rounded-2 box-shadow w-full">
          <div class="flex-center text-color">
            <InformationIcon width="25px" height="25px" />
          </div>
          <span class="text-sm text-color">Information</span>
        </div>
        <div @click="$router.push({ name: 'index' })"
          class="flex-center flex-column p-2 gap-2 bg-card rounded-2 box-shadow w-full">
          <div class="flex-center text-color">
            <ExchangeIcon width="25px" height="25px" />
          </div>
          <span class="text-sm text-color">Exchange</span>
        </div>
        <div @click="$router.push({ name: 'questions' })"
          class="flex-center flex-column p-2 gap-2 bg-card rounded-2 box-shadow w-full">
          <div class="flex-center text-color">
            <QuestionIcon width="25px" height="25px" />
          </div>
          <span class="text-sm text-color">Exchange</span>
        </div>
      </div>
    </footer>


  </div>

</template>

<script lang="ts" setup>
import { provide, ref } from "vue";
import ExchangeIcon from "@/components/icons/ExchangeIcon.vue";
import InformationIcon from "@/components/icons/InformationIcon.vue";
import QuestionIcon from "@/components/icons/QuestionIcon.vue";

const notifs = ref<Array<{ title; type }>>([]);
function createNotification(title: string, types: string) {
  notifs.value.push({ title: title, type: types });
}

provide("notification", createNotification);


</script>

<style>
.footer {
  left: 0;
  bottom: 0;
  position: fixed;
  max-height: 90px;
  z-index: var(--z-index-fixed);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.display {
  background: url("@/assets/images/background.png") no-repeat center center fixed;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.loader-bg {
  background: url("@/assets/images/loader-bg.png") no-repeat center center fixed;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

@keyframes l2 {
  to {
    transform: rotate(1turn);
  }
}

main {
  margin-bottom: 85px;
}

section {
  width: 100%;
}

.loader {
  width: 50px;
  aspect-ratio: 1;
  display: grid;
  border: 4px solid transparent;
  border-radius: 50%;
  border-right-color: hsl(var(--theme-color));
  animation: l15 1s infinite linear;
}

.loader::before,
.loader::after {
  content: "";
  grid-area: 1/1;
  margin: 2px;
  border: inherit;
  border-radius: 50%;
  animation: l15 2s infinite;
}

.loader::after {
  margin: 8px;
  animation-duration: 3s;
}

@keyframes l15 {
  100% {
    transform: rotate(1turn);
  }
}
</style>
