import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.degens777den.casino',
  appName: 'Degens777Den',
  webDir: 'build',
  server: {
    androidScheme: 'https',
    cleartext: true,
    allowNavigation: [
      '*',
      '*.kodakclout-prod.workers.dev',
      'localhost',
      '127.0.0.1'
    ]
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
    },
    CapacitorHttp: {
      enabled: true,
    },
  },
};

export default config;
