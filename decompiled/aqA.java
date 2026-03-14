/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  Fo
 *  aqG
 *  aqL
 *  azW
 *  org.apache.log4j.Logger
 */
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import org.apache.log4j.Logger;

class aqA {
    private static final Logger cQL = Logger.getLogger(aqA.class);
    private final aqL[] cQM;
    private final azW<String, aqM> cQN;
    private final String cQO;
    private final aqH cQP;

    aqA(String string, int n) {
        int n2;
        this.cQO = string;
        byte[] byArray = Fo.by((String)this.cQO);
        ByteBuffer byteBuffer = ByteBuffer.wrap(byArray);
        byteBuffer.order(ByteOrder.LITTLE_ENDIAN);
        int n3 = byteBuffer.getInt() + 756423;
        aqH aqH2 = new aqH(byteBuffer, n, n3);
        int n4 = aqH2.bGI();
        this.cQM = new aqL[n4];
        for (n2 = 0; n2 < n4; ++n2) {
            long l = aqH2.bGK();
            int n5 = aqH2.bGI();
            int n6 = aqH2.bGI();
            byte by = aqH2.aTf();
            this.cQM[n2] = new aqL(l, n5, n6, by);
        }
        n2 = aqH2.aTf();
        this.cQN = new azW(n2);
        for (int i = 0; i < n2; ++i) {
            aqM aqM2 = aqM.b(aqH2);
            this.cQN.f((Object)aqM2.cRh, (Object)aqM2);
        }
        ByteBuffer byteBuffer2 = byteBuffer.slice();
        byteBuffer2.order(byteBuffer.order());
        this.cQP = new aqH(byteBuffer2, n, n3);
    }

    public final String bGB() {
        return this.cQO;
    }

    private aqM fK(String string) {
        return (aqM)this.cQN.O((Object)string);
    }

    final boolean a(long l, aqz aqz2) {
        try {
            aqz2.reset();
            aqM aqM2 = (aqM)this.cQN.O((Object)"id");
            if (aqM2.gw(l) == 0) {
                cQL.warn((Object)("Pas de " + aqz2.getClass().getSimpleName() + " existant. id=" + l), (Throwable)new Exception());
                return false;
            }
            int n = aqM2.p(l, 0);
            this.a(this.cQM[n], aqz2);
            return true;
        }
        catch (Exception exception) {
            cQL.error((Object)("Probl\u00e8me  de lecture de " + aqz2.getClass().getSimpleName() + "id=" + l), (Throwable)exception);
            return false;
        }
    }

    private void a(aqL aqL2, aqz aqz2) {
        int n = aqL2.cRe;
        this.cQP.a(n, aqL2.cRg);
        aqz2.a(this.cQP);
        if ((long)(aqL2.cRf + n) != this.cQP.bGF()) {
            throw new Exception("Taille de donn\u00e9e incorrecte ");
        }
    }

    final <T extends aqz> void a(T t, aqG<T> aqG2) {
        for (aqL aqL2 : this.cQM) {
            t.reset();
            this.a(aqL2, t);
            aqG2.load(t);
        }
    }

    final <T extends aqz> void a(T t, String string, int n, aqG<T> aqG2) {
        aqM aqM2 = this.fK(string);
        int n2 = aqM2.gw(n);
        for (int i = 0; i < n2; ++i) {
            try {
                int n3 = aqM2.p(n, i);
                aqL aqL2 = this.cQM[n3];
                t.reset();
                this.a(aqL2, t);
                aqG2.load(t);
                continue;
            }
            catch (Exception exception) {
                cQL.error((Object)("Probl\u00e8me  de lecture de " + t.getClass().getSimpleName() + "id=" + n + "item num:" + i), (Throwable)exception);
            }
        }
    }

    public int bGC() {
        return this.cQM.length;
    }
}
