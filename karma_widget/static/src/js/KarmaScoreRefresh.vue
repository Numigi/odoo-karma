<template>
  <div class="karma-score-refresh" @click="onClicked()">
    <i class="fa fa-refresh"></i>
  </div>
</template>
<script>
export default {
  name: 'karma-score-refresh',
  props: {
    onClicked: {
      type: Function,
      required: true,
    },
  },
};
</script>
