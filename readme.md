# PlantUML Syntax

Simple syntax highlighting for plantuml files form sumlime_diagram_plugin

FileTypes: *.puml

![example](https://f.cloud.github.com/assets/23027/434215/b248d69c-af26-11e2-8743-33556d2da0fa.png)

## Helper

Convert json to plist xml:
```
plutil -convert xml1 puml.tmLanguage.json -o puml.tmLanguage
```

Get list of plantuml keywords:
```
java -jar plantuml.jar -language
```

## Resources

http://docs.sublimetext.info/en/latest/reference/syntaxdefs.html#compatibility-with-textmate
http://plantuml.sourceforge.net/developpers.html
http://manual.macromates.com/en/language_grammars
https://github.com/fluxsaas/sass-textmate-bundle/blob/master/Syntaxes/SASS.tmLanguage
https://github.com/Shammah/boo-sublime/blob/master/Boo.tmLanguage
