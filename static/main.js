const { createI18n } = VueI18n;

const i18n = createI18n({
    legacy: false,
    locale: 'ru',
    fallbackLocale: 'en',
    messages: {},
    missingWarn: false,      // <--- отключает предупреждения о пропавших ключах
    fallbackWarn: false,
})

async function loadLocale(langs) {
    for (const lang of langs) {
        const messages = await fetch(`/static/i18n/${lang}.json`).then(r => r.json())
        i18n.global.setLocaleMessage(lang, messages)
        i18n.global.locale.value = lang
    }
}

loadLocale(['en', 'kz', 'ru'])


function go_to(link) {
    window.open(link, '_blank')
}




