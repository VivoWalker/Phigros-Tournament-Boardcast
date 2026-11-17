#!/usr/bin/env python3
"""Capture README images from synthetic standard events; never open live data.

Requires npm ci, requirements-test.txt and Chromium. Run from any directory.
CHROME_BINARY can select an installed browser. Images go to docs/images/.
"""
from pathlib import Path
import os
import selectors
import shutil
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images'
SERVER = r"""
const fs=require('node:fs'),path=require('node:path');
const T=require('./lib/tournament'),Q=require('./public/js/qualifier-rules');
const s=require('./lib/default-state').createStandardState(),fixture=process.argv[2];
const act=(type,payload={})=>T.applyAction(s,{type,payload:T.CURRENT_MATCH_ACTIONS.has(type)?{matchId:s.tournament.currentMatchId,...payload}:payload});
s.event.title='Community Phigros Cup';s.event.organiser='Community event';s.event.venue='Demo venue';
act('set-competition-roster',{names:['Aster','Beryl','Cobalt','Delta','Echo','Fable','Glint','Halo','Iris','Jade','Kite','Lumen','Maple','Nova','Opal','Piper','Quartz','Rune','Sable','Terra','Vesper']});
if(fixture!=='setup'){
  act('set-qualifier-plan',{plan:'B'});
  for(const group of ['A','B'])for(const [i,p] of Q.entries(s,group).entries())act('set-qualifier-total',{group,playerId:p.id,total:2950000-i*18000});
  act('qualify',{verified:true});
  const regular=['W1','W2','W3','W4','W5','W6','L1','L2','W7','L3','L4','L5','L6'];
  for(const id of regular){
    act('select-match',{matchId:id});act('draw-candidates');
    const m=s.tournament.matches.find(m=>m.id===id);
    for(const playerIndex of [0,1])act('ban-song',{playerIndex,songId:m.candidates[playerIndex].id});
    act('pick-songs');
    if(fixture==='selection'){
      m.selectionPreviewCue.startedAt=Date.now()-60000;break;
    }
    for(let pi=0;pi<2;pi++)for(let si=0;si<2;si++)act('set-match-score',{playerIndex:pi,songIndex:si,score:pi?970000:990000,judgements:{accuracy:pi?97:99,perfect:pi?970:990,good:pi?30:10,bad:0,miss:0}});
    if(fixture==='control'){
      act('set-broadcast-cue',{stage:'double-elimination',scene:'double-elimination-processing',matchId:id,songIndex:1});break;
    }
    act('record-result',{verified:true});
  }
  if(fixture==='standings'){
    act('select-match',{matchId:'GF'});act('start-final-announcement');
    for(let pi=0;pi<2;pi++)for(let si=0;si<2;si++)act('set-match-score',{playerIndex:pi,songIndex:si,score:pi?980000:995000});
    act('record-result',{verified:true});
    act('set-broadcast-cue',{stage:'double-elimination',scene:'final-standings'});
  }
}
require('./lib/state-validation').validateState(s);
fs.writeFileSync(path.join(process.argv[1],'match-state.json'),JSON.stringify(s));
const app=require('./server').createBroadcastServer({dataDir:process.argv[1],preset:'standard',pin:'readme-main-fixture',scorekeeperPin:'readme-score-fixture',hostPin:'readme-host-fixture'});
app.listen(0,'127.0.0.1').then(a=>console.log(a.port));
process.on('SIGTERM',()=>app.close().then(()=>process.exit()));
"""


def capture(browser, fixture):
    with tempfile.TemporaryDirectory(prefix='phigros-readme-') as directory:
        process = subprocess.Popen(['node', '-e', SERVER, directory, fixture], cwd=ROOT,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        context = None
        try:
            with selectors.DefaultSelector() as ready:
                ready.register(process.stdout, selectors.EVENT_READ)
                if not ready.select(timeout=15):
                    raise RuntimeError('Screenshot fixture did not start')
            port = process.stdout.readline().strip()
            if not port.isdigit():
                raise RuntimeError(process.communicate(timeout=5)[1])
            base = 'http://127.0.0.1:' + port
            context = browser.new_context(viewport={'width': 1600, 'height': 1000}, reduced_motion='reduce')
            errors = []
            context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
            page = context.new_page()
            if fixture in ['setup', 'control']:
                page.goto(base + '/control/')
                page.fill('#pin', 'readme-main-fixture')
                page.click('#pair-form button')
                page.wait_for_selector('.production-workflow')
                if fixture == 'setup':
                    page.click('.tabs [data-tab="event"]')
                    panel = page.locator('.event-template-panel')
                    panel.scroll_into_view_if_needed()
                    page.evaluate('document.fonts.ready')
                    assert page.locator('#event-template-form button[type="submit"]').is_enabled()
                    panel.screenshot(path=str(OUT / 'event-template.jpg'), type='jpeg', quality=90)
                else:
                    preview = page.frame_locator('#program-preview')
                    preview.locator('#canvas[data-rendered-scene="double-elimination-processing"]').wait_for()
                    page.evaluate('document.fonts.ready')
                    assert page.locator('[data-score-editor="m"]').count() == 2
                    bottom = page.locator('[data-score-editor="m"]').evaluate_all('nodes=>Math.max(...nodes.map(n=>n.getBoundingClientRect().bottom))')
                    page.set_viewport_size({'width': 1600, 'height': max(1000, int(bottom) + 40)})
                    page.screenshot(path=str(OUT / 'control-panel.jpg'), type='jpeg', quality=90)
            else:
                scene = 'song-selection' if fixture == 'selection' else 'final-standings'
                page.set_viewport_size({'width': 1600, 'height': 900})
                page.goto(base + '/overlay/live.html?audio=0&bgm=0')
                page.wait_for_selector('#canvas[data-rendered-scene="' + scene + '"]')
                page.wait_for_function('document.querySelector("#scene")?.dataset.motionPhase==="idle"')
                page.evaluate('document.fonts.ready')
                page.wait_for_function('Array.from(document.querySelectorAll("#scene img")).every(i=>i.complete&&i.naturalWidth>0)')
                if fixture == 'selection':
                    assert page.locator('.candidate.picked').count() == 2
                else:
                    assert page.locator('[data-podium-place]').count() == 3
                page.screenshot(path=str(OUT / ('song-selection.jpg' if fixture == 'selection' else 'final-standings.jpg')), type='jpeg', quality=90)
            assert not errors, errors
            print('Captured ' + fixture, flush=True)
        finally:
            if context:
                context.close()
            process.terminate()
            try:
                process.communicate(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        binary = os.environ.get('CHROME_BINARY') or shutil.which('chromium')
        browser = p.chromium.launch(**({'executable_path': binary} if binary else {}), args=['--no-sandbox'])
        try:
            for fixture in ['setup', 'selection', 'control', 'standings']:
                capture(browser, fixture)
        finally:
            browser.close()


if __name__ == '__main__':
    main()
