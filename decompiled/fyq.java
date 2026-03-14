/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class fyq
implements aqz {
    protected int o;
    protected boolean tBA;
    protected HashMap<Integer, fyr> tBB;

    public int d() {
        return this.o;
    }

    public boolean gqt() {
        return this.tBA;
    }

    public HashMap<Integer, fyr> gqu() {
        return this.tBB;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tBA = false;
        this.tBB = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.tBA = aqH2.bxv();
        int n = aqH2.bGI();
        this.tBB = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            int n2 = aqH2.bGI();
            fyr fyr2 = new fyr();
            fyr2.a(aqH2);
            this.tBB.put(n2, fyr2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozL.d();
    }
}
