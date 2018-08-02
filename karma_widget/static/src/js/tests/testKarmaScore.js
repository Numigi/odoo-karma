
import test from "ava";
import Vue from "vue";
import KarmaScore from "../KarmaScore.vue";
import KarmaScoreHistory from "../KarmaScoreHistory.vue";
import KarmaScoreRefresh from "../KarmaScoreRefresh.vue";

Vue.component(KarmaScoreHistory.name, KarmaScoreHistory);
Vue.component(KarmaScoreRefresh.name, KarmaScoreRefresh);

test("Render KarmaScore with only a score and a label", (t) => {
    var Constructor = Vue.extend(KarmaScore);
    var vm = new Constructor({
        propsData: {
            score: "95.5",
            label: "Customer Score",
        }
    }).$mount();
    t.snapshot(vm.$el.outerHTML);
});

test("Render KarmaScore with history drilldown enabled", (t) => {
    var Constructor = Vue.extend(KarmaScore);
    var vm = new Constructor({
        propsData: {
            score: "95.5",
            label: "Customer Score",
            enableHistory: true,
            onHistoryClicked(){},
        }
    }).$mount();
    t.snapshot(vm.$el.outerHTML);
});

test("Render KarmaScore with refresh enabled", (t) => {
    var Constructor = Vue.extend(KarmaScore);
    var vm = new Constructor({
        propsData: {
            score: "95.5",
            label: "Customer Score",
            enableRefresh: true,
            onRefreshClicked(){},
        }
    }).$mount();
    t.snapshot(vm.$el.outerHTML);
});

test("When clicking on Refresh, then refresh callback is called.", async (t) => {
    var onRefreshCalled = false;

    var Constructor = Vue.extend(KarmaScore);
    var vm = new Constructor({
        propsData: {
            score: "",
            label: "",
            enableRefresh: true,
            onRefreshClicked(){
                onRefreshCalled = true;
            },
        }
    }).$mount();

    vm.$el.querySelector(".karma-score-refresh").click();
    await vm.$nextTick();

    t.true(onRefreshCalled);
});

test("When clicking on History, then history callback is called.", async (t) => {
    var onHistoryCalled = false;

    var Constructor = Vue.extend(KarmaScore);
    var vm = new Constructor({
        propsData: {
            score: "",
            label: "",
            enableHistory: true,
            onHistoryClicked(){
                onHistoryCalled = true;
            },
        }
    }).$mount();

    vm.$el.querySelector(".karma-score-history").click();
    await vm.$nextTick();

    t.true(onHistoryCalled);
});

