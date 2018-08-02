<template>
  <div class="karma-score-history" @click="onClicked()">
    {{ label }}
  </div>
</template>
<script>
export default {
  name: "karma-score-history",
  props: {
    onClicked: {
      type: Function,
      required: true,
    },
    label: {
      type: String,
      default: "History",
    },
  },
};
</script>
