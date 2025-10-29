const header_template = `
<div class="header">
  <div class="logo__wraper" >
    <select id="model-select" style="font-size: 2em!important;" class="lang-select nav-link" @change="onModelChange" v-model="member_model">
        <template v-for="model in members">
            <option :value="model">{{model}}</option>
        </template>
    </select>
  </div>
  <ul class="nav nav-links">
<!--    <li class="nav-item">-->
<!--      <a class="nav-link  active" href="index.html">Главная страница</a>-->
<!--    </li>-->
    
<!--    <li class="nav-item">-->
<!--        <select class="lang-select nav-link" @change="onModelChange" v-model="member_model">-->
<!--        <template v-for="model in members">-->
<!--            <option :value="model">{{model}}</option>-->
<!--        </template>-->
<!--        </select>-->
<!--    </li>-->
    <li class="nav-item">
        <select id="lang-select" style="font-size: 1.5em!important;" class="lang-select nav-link" v-model="$i18n.locale">
        <template v-for="lang in languages">
            <option :value="lang.key">{{lang.label}}</option>
        </template>
        </select>
    </li>
    
  </ul>
</div>
`;

const MyHeader = {
    template: header_template,
    data() {
        return {
            languages: [
                {key: 'ru', label: 'ru'},
                {key: 'kz', label: 'kz'},
                {key: 'en', label: 'en'}
            ],
            member_model: 9
        }
    },
    methods: {
        go_to(link) {
            if (typeof go_to === 'function') {
                go_to(link);
            }
        },
        onModelChange() {
            this.$emit('model_change', this.member_model);
        }
    },
    emits: ['model_change'],
    props: [
        'members'
    ],
};

window.registerHeaderComponent = function(app_instance) {
    app_instance.component('my-header', MyHeader);
}
