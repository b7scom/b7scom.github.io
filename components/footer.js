const footer_template = `
<footer>
    <template v-for="soc in social_medias" :key="soc.key">
        <div class="contact-kart" @click="go_to(soc.link)">
          <div class="contact-logo">
            <img class="logo" :src="'static/socmedia/' + soc.img">
          </div>
          <div class="contact-wraper">
            <span :class="soc.key">{{ soc.username }}</span>
          </div>
        </div>
    </template>
</footer>
`;

const MyFooter = {
    template: footer_template,
    data() {
        return {
            social_medias: [
                // {
                //     key: 'telegram',
                //     link: 'https://t.me/iCargoLife',
                //     label: 'telegram',
                //     username: 'iCargoLife',
                //     img: 'telegram.png'
                // },
                {
                    key: 'instagram',
                    link: 'https://www.instagram.com/kulbanu.baibulatova1/',
                    label: 'instagram',
                    username: 'kulbanu.baibulatova1',
                    img: 'instagram.png'
                },
                {
                    key: 'whatsapp',
                    link: 'https://wa.me/77773042162',
                    label: 'Whatsapp',
                    username: '77773042162',
                    img: 'whatsapp.gif'
                },
                {
                    key: 'phone',
                    link: 'tel:+77773042162',
                    label: 'phone',
                    username: '+77773042162',
                    img: 'phone.png'
                }
            ]
        }
    },
    methods: {
        go_to(link) {
            if (typeof go_to === 'function') {
                go_to(link);
            }
        }
    }
};

window.registerFooterComponent = function(app_instance) {
    app_instance.component('my-footer', MyFooter);
}
