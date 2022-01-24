package im.status.ethereum;

import android.content.Context;
import android.util.Log;
import androidx.annotation.NonNull;

import com.bumptech.glide.Glide;
import com.bumptech.glide.Registry;
import com.bumptech.glide.annotation.Excludes;
import com.bumptech.glide.annotation.GlideModule;
import com.bumptech.glide.integration.okhttp3.OkHttpUrlLoader;
import com.bumptech.glide.load.model.GlideUrl;
import com.bumptech.glide.module.AppGlideModule;
import com.dylanvann.fastimage.FastImageOkHttpProgressGlideModule;
import com.facebook.react.modules.network.OkHttpClientProvider;

import okhttp3.OkHttpClient;
import okhttp3.Interceptor;

import java.io.InputStream;
import java.lang.RuntimeException;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.security.SecureRandom;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

@Excludes({com.dylanvann.fastimage.FastImageOkHttpProgressGlideModule.class, com.bumptech.glide.integration.okhttp3.OkHttpLibraryGlideModule.class})
@GlideModule
public class StatusGlide extends AppGlideModule {
  @Override
  public void registerComponents(@NonNull Context context, @NonNull Glide glide, @NonNull Registry registry) {
    Interceptor interceptor;

    try {
      final Class<?> rplIf = Class.forName("com.dylanvann.fastimage.FastImageOkHttpProgressGlideModule$ResponseProgressListener");
      final Field plField = FastImageOkHttpProgressGlideModule.class.getDeclaredField("progressListener");
      final Method interceptorMethod = FastImageOkHttpProgressGlideModule.class.getDeclaredMethod("createInterceptor", rplIf);
      plField.setAccessible(true);
      interceptorMethod.setAccessible(true);

      interceptor = (Interceptor) interceptorMethod.invoke(null, plField.get(null));
    } catch(Exception e) {
      //TODO: handle this
      Log.e("StatusGlide", "Could not initialize OkHttpClient");
      interceptor = null;
    }

    // replace with okhttp-tls and accept all system CA + our cert
    final TrustManager[] trustNoCerts = new TrustManager[]{
      new X509TrustManager() {
        @Override
        public void checkClientTrusted(X509Certificate[] chain, String authType) throws CertificateException {
          throw new CertificateException("Trust no one");
        }

        @Override
        public void checkServerTrusted(X509Certificate[] chain, String authType) throws CertificateException {
          throw new CertificateException("Trust no one");
        }

        @Override
        public X509Certificate[] getAcceptedIssuers() {
            return new X509Certificate[]{};
        }
      }
    };

    SSLSocketFactory sslSocketFactory;

    try {
      final SSLContext sslContext = SSLContext.getInstance("SSL");
      sslContext.init(null, trustNoCerts, new SecureRandom());
      sslSocketFactory = sslContext.getSocketFactory();
    } catch(Exception e) {
      sslSocketFactory = null;
    }

    OkHttpClient client = OkHttpClientProvider
      .getOkHttpClient()
      .newBuilder()
      .addInterceptor(interceptor)
      .sslSocketFactory(sslSocketFactory, (X509TrustManager) trustNoCerts[0])
      .build();
    OkHttpUrlLoader.Factory factory = new OkHttpUrlLoader.Factory(client);
    registry.replace(GlideUrl.class, InputStream.class, factory);
  }
}
