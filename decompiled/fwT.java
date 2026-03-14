/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class fwT
implements aqz {
    protected int o;
    protected int[] tAD;
    protected HashMap<Integer, Integer> tAE;
    protected int[] tAd;

    public int d() {
        return this.o;
    }

    public int[] gpw() {
        return this.tAD;
    }

    public HashMap<Integer, Integer> gpx() {
        return this.tAE;
    }

    public int[] goX() {
        return this.tAd;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tAD = null;
        this.tAE = null;
        this.tAd = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.tAD = aqH2.bGM();
        int n = aqH2.bGI();
        this.tAE = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            int n2 = aqH2.bGI();
            int n3 = aqH2.bGI();
            this.tAE.put(n2, n3);
        }
        this.tAd = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.ozj.d();
    }
}
