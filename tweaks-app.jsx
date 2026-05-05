// Tweaks app for Aegis Group — 3D Earth + GSAP version

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accentColor": "blue",
  "companyName": "Storm Colleton & Associates",
  "showGlobe": true
}/*EDITMODE-END*/;

function TweaksApp() {
  const { useTweaks, TweaksPanel, TweakSection, TweakText, TweakRadio, TweakToggle } = window;
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);

  React.useEffect(() => {
    document.querySelectorAll('.nav-logo-text, .footer-logo-text').forEach(el => {
      el.textContent = tweaks.companyName;
    });
  }, [tweaks.companyName]);

  React.useEffect(() => {
    const root = document.documentElement;
    if (tweaks.accentColor === 'olive') {
      root.style.setProperty('--blue', '#8a9460');
      root.style.setProperty('--blue-b', '#a3ad75');
      root.style.setProperty('--blue-dim', 'rgba(138,148,96,0.13)');
      root.style.setProperty('--border-b', 'rgba(138,148,96,0.28)');
      root.style.setProperty('--cyan', '#c5cf95');
    } else if (tweaks.accentColor === 'blue') {
      root.style.setProperty('--blue', '#5e6ad2');
      root.style.setProperty('--blue-b', '#7b8cef');
      root.style.setProperty('--blue-dim', 'rgba(94,106,210,0.11)');
      root.style.setProperty('--border-b', 'rgba(94,106,210,0.22)');
      root.style.setProperty('--cyan', '#4cc9f0');
    } else if (tweaks.accentColor === 'gold') {
      root.style.setProperty('--blue', 'oklch(64% 0.1 75)');
      root.style.setProperty('--blue-b', 'oklch(74% 0.09 80)');
      root.style.setProperty('--blue-dim', 'oklch(64% 0.1 75 / 0.12)');
      root.style.setProperty('--border-b', 'oklch(64% 0.1 75 / 0.28)');
      root.style.setProperty('--cyan', 'oklch(80% 0.08 90)');
    } else if (tweaks.accentColor === 'teal') {
      root.style.setProperty('--blue', '#0d9488');
      root.style.setProperty('--blue-b', '#2dd4bf');
      root.style.setProperty('--blue-dim', 'rgba(13,148,136,0.1)');
      root.style.setProperty('--border-b', 'rgba(13,148,136,0.25)');
      root.style.setProperty('--cyan', '#67e8f9');
    }
  }, [tweaks.accentColor]);

  React.useEffect(() => {
    const s = document.getElementById('globe-section');
    const divs = document.querySelectorAll('#globe-section + .divider');
    if (s) s.style.display = tweaks.showGlobe ? '' : 'none';
    divs.forEach(d => d.style.display = tweaks.showGlobe ? '' : 'none');
  }, [tweaks.showGlobe]);

  return (
    <TweaksPanel>
      <TweakSection label="Brand">
        <TweakText
          label="Company Name"
          value={tweaks.companyName}
          onChange={v => setTweak('companyName', v)}
        />
      </TweakSection>
      <TweakSection label="Accent Color">
        <TweakRadio
          label="Tone"
          value={tweaks.accentColor}
          options={[
            { label: 'Olive', value: 'olive' },
            { label: 'Blue', value: 'blue' },
            { label: 'Gold', value: 'gold' },
            { label: 'Teal', value: 'teal' },
          ]}
          onChange={v => setTweak('accentColor', v)}
        />
      </TweakSection>
      <TweakSection label="Sections">
        <TweakToggle
          label="3D Globe / Operations"
          value={tweaks.showGlobe}
          onChange={v => setTweak('showGlobe', v)}
        />
      </TweakSection>
    </TweaksPanel>
  );
}

const _aegisMount = document.createElement('div');
document.body.appendChild(_aegisMount);
ReactDOM.createRoot(_aegisMount).render(<TweaksApp />);
