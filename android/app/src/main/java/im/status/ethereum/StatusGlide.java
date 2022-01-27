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
import okhttp3.tls.HandshakeCertificates;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.lang.RuntimeException;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

import im.status.ethereum.module.StatusPackage;


/*import java.security.cert.CertificateException;
import java.security.SecureRandom;
import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;*/

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

    String certPem = StatusPackage.getImageTLSCert();
    X509Certificate cert;

    try {
      CertificateFactory cf = CertificateFactory.getInstance("X.509");
      cert = (X509Certificate) cf.generateCertificate(new ByteArrayInputStream(certPem.getBytes()));
    } catch(Exception e) {
      Log.e("StatusGlide", "Could not parse certificate");
      cert = null;
    }

    HandshakeCertificates clientCertificates = new HandshakeCertificates.Builder()
      .addPlatformTrustedCertificates()
      .addTrustedCertificate(cert)
      .build();

    OkHttpClient client = OkHttpClientProvider
      .getOkHttpClient()
      .newBuilder()
      .addInterceptor(interceptor)
      .sslSocketFactory(clientCertificates.sslSocketFactory(), clientCertificates.trustManager())
      .build();

    OkHttpUrlLoader.Factory factory = new OkHttpUrlLoader.Factory(client);
    registry.replace(GlideUrl.class, InputStream.class, factory);
  }
}
