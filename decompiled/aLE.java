/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class aLE
implements aqz {
    protected short aZk;
    protected HashMap<Byte, Float> eiE;

    public short aWP() {
        return this.aZk;
    }

    public HashMap<Byte, Float> clV() {
        return this.eiE;
    }

    @Override
    public void reset() {
        this.aZk = 0;
        this.eiE = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.aZk = aqH2.bGG();
        int n = aqH2.bGI();
        this.eiE = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            byte by = aqH2.aTf();
            float f = aqH2.bGH();
            this.eiE.put(by, Float.valueOf(f));
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyG.d();
    }
}
