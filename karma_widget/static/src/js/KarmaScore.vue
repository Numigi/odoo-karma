<template>
  <div id="karma-score">
    <karma-score-refresh v-if="enableRefresh" :on-clicked="onRefreshClicked"/>
    <div id="karma-score__score">{{ score }}</div>
    <div id="karma-score__label">{{ label }}</div>
    <karma-score-history v-if="enableHistory" :on-clicked="onHistoryClicked" :label="historyLabel"/>
  </div>
</template>
<script>
export default {
  name: "karma-score",
  props: {
    score: {
      // The score is a string containing the decimal number already formated.
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    enableRefresh: {
      type: Boolean,
      default: false,
    },
    onRefreshClicked: {
      type: Function,
    },
    enableHistory: {
      default: false,
    },
    historyLabel: {
      type: String,
    },
    onHistoryClicked: {
      type: Function,
    },
  },
};
</script>
