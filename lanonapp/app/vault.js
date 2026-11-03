/* LaNonApp vault v0.9.0, AGPL-3.0-or-later. No remote sync, no clinical use. */
(function(root,factory){const v=factory();if(typeof module!=="undefined"&&module.exports)module.exports=v;if(root)root.LaNonVault=v})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const ITERATIONS=310000,enc=new TextEncoder(),dec=new TextDecoder();
function sub(){if(!globalThis.crypto?.subtle)throw Error("WebCrypto requiere HTTPS");return crypto.subtle}
function rand(n){let x=new Uint8Array(n);crypto.getRandomValues(x);return x}
function b64(x){let s="";for(const v of new Uint8Array(x))s+=String.fromCharCode(v);return btoa(s)}
function bin(x){if(typeof x!=="string"||!/^[a-zA-Z0-9+/]*={0,2}$/.test(x))throw Error("Codificación incorrecta");return Uint8Array.from(atob(x),c=>c.charCodeAt(0))}
async function derive(pass,salt,iterations=ITERATIONS){if(typeof pass!=="string"||pass.length<10)throw Error("La frase de acceso requiere 10 caracteres");if(salt.length!==16||iterations<250000||iterations>2000000)throw Error("Parámetros de derivación no válidos");let input=await sub().importKey("raw",enc.encode(pass),"PBKDF2",false,["deriveKey"]);return sub().deriveKey({name:"PBKDF2",hash:"SHA-256",salt,iterations},input,{name:"AES-GCM",length:256},false,["encrypt","decrypt"])}
async function seal(key,data){let iv=rand(12),cipher=await sub().encrypt({name:"AES-GCM",iv,additionalData:enc.encode("LaNonApp-vault-v1")},key,enc.encode(JSON.stringify(data)));return {iv:b64(iv),ciphertext:b64(cipher)}}
async function open(key,doc){if(doc.version!==1||!doc.iv||!doc.ciphertext)throw Error("Bóveda incompatible");const iv=bin(doc.iv);if(iv.length!==12)throw Error("IV inválido");try{return JSON.parse(dec.decode(await sub().decrypt({name:"AES-GCM",iv,additionalData:enc.encode("LaNonApp-vault-v1")},key,bin(doc.ciphertext))))}catch{throw Error("Frase incorrecta o archivo dañado")}}
async function create(pass,data){let salt=rand(16),key=await derive(pass,salt),body=await seal(key,data);return {key,doc:{version:1,kdf:"PBKDF2-SHA256",iterations:ITERATIONS,salt:b64(salt),...body}}}
async function unlock(pass,doc){if(!doc||doc.version!==1||doc.kdf!=="PBKDF2-SHA256")throw Error("Bóveda incompatible");let key=await derive(pass,bin(doc.salt),doc.iterations),data=await open(key,doc);return {key,data}}
async function reseal(key,doc,data){if(!doc||doc.version!==1)throw Error("Bóveda ausente");return {...doc,...await seal(key,data)}}
return {create,unlock,reseal};
});