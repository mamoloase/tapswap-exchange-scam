<template>
    <svg :width="props.width" :height="props.height" :fill="props.fill" class="bi bi-caret-down-fill" viewBox="0 0 16 16">
        <path d="M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"/>
    </svg>

</template>

<script setup lang="ts">
interface Props {
    width?: string,
    height?: string,
    fill?: string,
}
const props = withDefaults(defineProps<Props>(), {
    width: "20px",
    height: "20px",
    fill: "currentColor"
});
</script>