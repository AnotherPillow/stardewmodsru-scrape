let html = ``
import mods from './mods.json' with { type: 'json' }

let flatMods = []
Object.keys(mods).forEach(k => {
    const list = mods[k]
    flatMods = [ ...flatMods, ...list]
})

html += `<!DOCTYPE HTML><html><body>`
html += `<h1>Mods on stardewmods.ru</h1>`
html += `<h2>Count: ${flatMods.length}</h2>`
html += `<ul>`

// for (const mod of mods) {
for (let i = 0; i < flatMods.length; i++) {
    const mod = flatMods[i]
    const files = Object.keys(mod).filter(k => k.startsWith('full_file_')).map(k => mod[k])

    const filesHtml = files.map(file => `
        <li id="mod-${i}-file-${file.name}">
            <fieldset>
                <legend><a href="${file.href}">${file.name} (${file.size.replace("Б", "B")})<a></legend>
                <p>${file.download_count} downloads.</p>
                <p>Uploaded: ${file.uploaded}</p>
                <p>${file.description_html.replaceAll("\n","<br>").replaceAll("\t", "").replaceAll("<img", "&lt;img")}</p>
            </fieldset>
        </li>
    `)

    html += `
        <li>
            <fieldset>
                <legend><a href="${mod.preview_href}"><h2>${mod.preview_title}</h2></a></legend>
                
                <p>${mod.preview_description?.replaceAll("\n","<br>").replaceAll("\t", "").replaceAll("<img", "&lt;img")}</p>
                <img align="right" src="${mod.preview_image}" height="200" loading="lazy">

                <ul>
                    ${filesHtml.join('\n')}
                </ul>
            </fieldset>
        </li>
    `
}

html += `</ul></body></html>`


Bun.file('list.html').write(html)
