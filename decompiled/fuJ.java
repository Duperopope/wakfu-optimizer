/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class fuJ
implements aqz {
    protected int o;
    protected fuK[] tyL;
    protected fuK[] tyM;
    protected HashMap<Short, Byte> ehE;
    protected HashMap<Short, Byte> ehF;

    public int d() {
        return this.o;
    }

    public fuK[] gnE() {
        return this.tyL;
    }

    public fuK[] gnF() {
        return this.tyM;
    }

    public HashMap<Short, Byte> ckU() {
        return this.ehE;
    }

    public HashMap<Short, Byte> ckV() {
        return this.ehF;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tyL = null;
        this.tyM = null;
        this.ehE = null;
        this.ehF = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        int n3;
        this.o = aqH2.bGI();
        int n4 = aqH2.bGI();
        this.tyL = new fuK[n4];
        for (n3 = 0; n3 < n4; ++n3) {
            this.tyL[n3] = new fuK();
            this.tyL[n3].a(aqH2);
        }
        n3 = aqH2.bGI();
        this.tyM = new fuK[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tyM[n2] = new fuK();
            this.tyM[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.ehE = new HashMap(n2);
        for (n = 0; n < n2; ++n) {
            short s = aqH2.bGG();
            byte by = aqH2.aTf();
            this.ehE.put(s, by);
        }
        n = aqH2.bGI();
        this.ehF = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            short s = aqH2.bGG();
            byte by = aqH2.aTf();
            this.ehF.put(s, by);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAA.d();
    }
}
