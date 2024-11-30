<template>
    <section class="mt-3 mb-5">
        <div class="flex-center gap-2 flex-column text-center">
            <h1 class="text-lg text-color text-shadow">F A Q</h1>
            <span class="text-sm description-color">
                This section is dedicated to FAQ. For additional information, you can always contact our support team.
            </span>
        </div>
    </section>
    <section>
        <div class="flex-center flex-column w-full gap-2">
            <div @click="selected == question.id ? selected = 0 : selected = question.id" class="d-flex bg-card flex-column w-full p-2 rounded-1" v-for="question in questions">
                <span class="text-sm text-color text-shadow">{{ question.question }}</span>

                <div v-if="question.id == selected" class="mt-2">
                    <span class="text-sm description-color">{{ question.answer }}</span>
                </div>
            </div>
            
        </div>
    </section>
    
</template>

<script setup>
import { ref } from "vue";

const questions = ref([
    { id: 1, question: 'How many coins can I exchange?' ,answer : 'At the moment, our 24-hour exchange limit is almost 670 million TAPS coins.'},
    { id: 2, question: 'How many coins can I exchange?' ,answer : 'At the moment, our 24-hour exchange limit is almost 670 million TAPS coins.'},

]);
const selected = ref(0);

</script>